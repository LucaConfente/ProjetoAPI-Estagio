# src/http_client.py
import requests
import json
import time
import logging
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException

# Assumindo que as exceções customizadas estão definidas em src.exceptions
from src.exceptions import (
    OpenAIAPIError,
    OpenAIAuthenticationError,
    OpenAIBadRequestError,
    OpenAINotFoundError,
    OpenAIRateLimitError,
    OpenAIServerError,
    OpenAIClientError,
    OpenAITimeoutError,
    OpenAIConnectionError,
    OpenAIRetryError,
)
from src.config import Config

logger = logging.getLogger(__name__)

class ClienteHttpOpenAI:
    def __init__(self, max_tentativas: int = 2, fator_backoff: float = 0.01, tempo_limite: int = 10, max_requisicoes_por_segundo: float = 3.0):
        """
        Inicializa o cliente HTTP para OpenAI.
        Args:
            max_tentativas (int): Número máximo de tentativas de retry para erros temporários (default: 2).
            fator_backoff (float): Fator inicial para cálculo do backoff exponencial em segundos (default: 0.01).
            tempo_limite (int): Timeout em segundos para cada requisição (default: 10).
            max_requisicoes_por_segundo (float): Limite de requisições por segundo (rate limit local, default: 3.0).
        """
        self.configuracao = Config.get_instance()
        self.chave_api = self.configuracao.OPENAI_API_KEY
        self.url_base = "https://api.openai.com/v1"
        self.tempo_limite = tempo_limite
        self.max_tentativas = max_tentativas
        self.fator_backoff = fator_backoff
        self.sessao = requests.Session()
        self.sessao.headers.update({"Authorization": f"Bearer {self.chave_api}"})

        # --- Rate Limiter (Token Bucket) ---
        self.max_requisicoes_por_segundo = max_requisicoes_por_segundo
        self._tokens = self.max_requisicoes_por_segundo
        self._ultimo_token = time.time()

    def _tratar_erro_resposta(self, resposta: requests.Response):
        """
        Trata as respostas de erro da API e levanta exceções customizadas.
        Este método é chamado para erros HTTP que NÃO são retentáveis (ex: 400, 401, 404, 403)
        ou para o erro final após o esgotamento das retries.
        """
        from src.http_status_reasons import HTTP_STATUS_REASONS
        codigo_status = resposta.status_code
        reason = resposta.reason or HTTP_STATUS_REASONS.get(codigo_status, "Unknown Error")
        mensagem_erro = f"{codigo_status} - {reason}"
        error_details = None

        try:
            json_erro = resposta.json()
            if "error" in json_erro:
                error_details = json_erro["error"]
                mensagem_erro += f" | Detalhes da API: {error_details.get('message', 'N/A')}"
        except json.JSONDecodeError:
            mensagem_erro += f" | Corpo da resposta não-JSON: {resposta.text[:200]}..."

        if codigo_status in (401, 403):
            raise OpenAIAuthenticationError(mensagem_erro, status_code=codigo_status, error_details=error_details)
        elif codigo_status == 400:
            raise OpenAIBadRequestError(mensagem_erro, status_code=codigo_status, error_details=error_details)
        elif codigo_status == 404:
            raise OpenAINotFoundError(mensagem_erro, status_code=codigo_status, error_details=error_details)
        elif codigo_status == 429:
            raise OpenAIRateLimitError(mensagem_erro, status_code=codigo_status, error_details=error_details)
        elif codigo_status >= 500:
            raise OpenAIServerError(mensagem_erro, status_code=codigo_status, error_details=error_details)
        else:
            raise OpenAIAPIError(mensagem_erro, status_code=codigo_status, error_details=error_details)


    def _rate_limiter(self):
        """
        Rate limiter simples (token bucket): permite até N requisições por segundo.
        Se não houver tokens disponíveis, aguarda até liberar.
        """
        agora = time.time()
        tokens_para_adicionar = (agora - self._ultimo_token) * self.max_requisicoes_por_segundo
        if tokens_para_adicionar > 0:
            self._tokens = min(self.max_requisicoes_por_segundo, self._tokens + tokens_para_adicionar)
            self._ultimo_token = agora
        if self._tokens >= 1:
            self._tokens -= 1
            return
        tempo_espera = (1 - self._tokens) / self.max_requisicoes_por_segundo
        logger.info(f"Rate limit atingido. Aguardando {tempo_espera:.2f}s para próxima requisição...")
        time.sleep(tempo_espera)
        self._tokens = 0
        self._ultimo_token = time.time()

    def _realizar_requisicao(self, metodo: str, ponto_final: str, **kwargs) -> dict:
        """
        Realiza uma requisição HTTP para a API da OpenAI com lógica de retry e backoff.
        """
        url_completa = f"{self.url_base}/{ponto_final}"
        kwargs.setdefault('timeout', self.tempo_limite)
        
        last_caught_custom_exception = None # Armazena a última exceção customizada capturada no loop

        for tentativa in range(self.max_tentativas + 1):
            self._rate_limiter()  # Aplica rate limit antes de cada requisição
            try:
                resposta = self.sessao.request(metodo, url_completa, **kwargs)
                resposta.raise_for_status() # Levanta HTTPError para 4xx/5xx

                try:
                    return resposta.json()
                except json.JSONDecodeError:
                    logger.warning(f"Resposta da API não é JSON para {url_completa}. Conteúdo: {resposta.text[:100]}...")
                    return {"mensagem": "Requisição bem-sucedida, mas resposta não é JSON", "resposta_bruta": resposta.text}

            except Timeout as e:
                last_caught_custom_exception = OpenAITimeoutError("Tempo limite excedido na conexão com a API OpenAI.", original_exception=e)
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Tempo limite. Re-tentando...")

            except ConnectionError as e:
                last_caught_custom_exception = OpenAIConnectionError(f"Erro de conexão para {url_completa}", original_exception=e)
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro de conexão. Re-tentando...")

            except HTTPError as e:
                # Para 429 e 5xx, armazenamos a exceção customizada específica para potencial retry
                if e.response.status_code == 429:
                    from src.http_status_reasons import HTTP_STATUS_REASONS
                    reason = e.response.reason or HTTP_STATUS_REASONS.get(e.response.status_code, "Unknown Error")
                    error_details = e.response.json().get('error') if e.response.content else None
                    mensagem_erro = f"Erro na API da OpenAI: {e.response.status_code} - {reason}"
                    if error_details and 'message' in error_details:
                        mensagem_erro += f" Detalhes da API: {error_details['message']}"
                    last_caught_custom_exception = OpenAIRateLimitError(
                        mensagem_erro,
                        status_code=e.response.status_code,
                        error_details=error_details,
                        original_exception=e
                    )
                    logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro HTTP 429. Re-tentando...")
                elif e.response.status_code >= 500:
                    from src.http_status_reasons import HTTP_STATUS_REASONS
                    reason = e.response.reason or HTTP_STATUS_REASONS.get(e.response.status_code, "Unknown Error")
                    error_details = e.response.json().get('error') if e.response.content else None
                    mensagem_erro = f"Erro na API da API: {e.response.status_code} - {reason}"
                    if error_details and 'message' in error_details:
                        mensagem_erro += f" Detalhes da API: {error_details['message']}"
                    last_caught_custom_exception = OpenAIServerError(
                        mensagem_erro,
                        status_code=e.response.status_code,
                        error_details=error_details,
                        original_exception=e
                    )
                    logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro HTTP {e.response.status_code}. Re-tentando...")
                else:
                    # Para outros erros 4xx (ex: 400, 401, 403, 404), não retente. Levante imediatamente.
                    # Este método levantará uma exceção e sairá da função.
                    self._tratar_erro_resposta(e.response)

            except RequestException as e: # Captura outras exceções relacionadas a requests (ex: TooManyRedirects)
                last_caught_custom_exception = OpenAIClientError(f"Erro de requisição inesperado para {url_completa}", original_exception=e)
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro de requisição inesperado. Re-tentando...")

            except Exception as e: # Captura quaisquer outros erros inesperados
                last_caught_custom_exception = OpenAIClientError(f"Erro inesperado durante a requisição para {url_completa}", details=str(e), original_exception=e)
                logger.error(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro inesperado. Re-tentando...", exc_info=True)

            # Se uma exceção customizada foi capturada e ainda há retries disponíveis
            if last_caught_custom_exception and tentativa < self.max_tentativas:
                tempo_espera = self.fator_backoff * (2 ** tentativa)
                logger.info(f"Aguardando {tempo_espera:.2f} segundos antes da próxima tentativa...")
                time.sleep(tempo_espera)
                # Não limpe last_caught_custom_exception aqui, ela será sobrescrita na próxima iteração
                # se um novo erro ocorrer.
            elif last_caught_custom_exception:
                # Não há mais retries, ou max_tentativas era 0 desde o início.
                # Levante a exceção apropriada.
                if self.max_tentativas == 0:
                    # Se nenhuma retry foi configurada, levante o erro específico diretamente
                    raise last_caught_custom_exception
                else:
                    # Se retries foram configuradas e esgotadas, encapsule em OpenAIRetryError
                    # Sempre levante OpenAIRetryError ao esgotar tentativas
                    # Se for erro HTTP customizado, encapsule a exceção original do pacote requests
                    if hasattr(last_caught_custom_exception, 'original_exception') and isinstance(last_caught_custom_exception.original_exception, requests.exceptions.HTTPError):
                        raise OpenAIRetryError(
                            f"Máximo de retries ({self.max_tentativas}) excedido para {url_completa}",
                            original_exception=last_caught_custom_exception.original_exception
                        )
                    else:
                        raise OpenAIRetryError(
                            f"Máximo de retries ({self.max_tentativas}) excedido para {url_completa}",
                            original_exception=last_caught_custom_exception
                        )
        
        # Se o loop terminar sem retornar (o que não deveria acontecer se todos os caminhos forem cobertos)
        raise OpenAIClientError("Erro desconhecido: A requisição falhou sem exceção capturada e sem retorno de dados.")

    def obter(self, ponto_final: str, parametros: dict = None) -> dict:
        return self._realizar_requisicao("GET", ponto_final, params=parametros)

    def enviar(self, ponto_final: str, dados: dict = None) -> dict:
        return self._realizar_requisicao("POST", ponto_final, json=dados)

    def atualizar(self, ponto_final: str, dados: dict = None) -> dict:
        return self._realizar_requisicao("PUT", ponto_final, json=dados)

    def deletar(self, ponto_final: str) -> dict:
        return self._realizar_requisicao("DELETE", ponto_final)