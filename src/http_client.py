
import requests
import json
import time
import logging
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException

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
    def obter(self, ponto_final: str, params: dict = None) -> dict:
        """
        Realiza uma requisição GET para o endpoint especificado.
        Args:
            ponto_final (str): Endpoint da API (ex: 'models').
            params (dict): Parâmetros de consulta opcionais.
        Returns:
            dict: Resposta da API em formato JSON.
        """
        return self._realizar_requisicao("GET", ponto_final, params=params)

    def enviar(self, ponto_final: str, dados: dict = None) -> dict:
        """
        Realiza uma requisição POST para o endpoint especificado.
        Args:
            ponto_final (str): Endpoint da API (ex: 'chat/completions').
            dados (dict): Dados para envio no corpo da requisição.
        Returns:
            dict: Resposta da API em formato JSON.
        """
        headers = {"Content-Type": "application/json"}
        return self._realizar_requisicao("POST", ponto_final, json=dados, headers=headers)
    
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

        # --- Métricas de uso ---
        self.metricas = {
            'total_requisicoes': 0,
            'requisicoes_sucesso': 0,
            'requisicoes_falha': 0,
            'tempo_total': 0.0,
            'ultimos_status': [],
        }
       
        #BACKOFF 

        self._backoff_calls = []

    def get_metricas(self):
        """Retorna as métricas de uso do cliente HTTP."""
        return self.metricas.copy()

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
        self._backoff_calls.clear()  # Clear previous backoff intervals before each request
        url_completa = f"{self.url_base}/{ponto_final}"
        kwargs.setdefault('timeout', self.tempo_limite)
        last_caught_custom_exception = None
        for tentativa in range(self.max_tentativas + 1):
            self._rate_limiter()
            inicio = time.time()
            status = None
            last_caught_custom_exception = None
            try:
                resposta = self.sessao.request(metodo, url_completa, **kwargs)
                resposta.raise_for_status()
                try:
                    resultado = resposta.json()
                except json.JSONDecodeError:
                    resultado = {"mensagem": "Requisição bem-sucedida, mas resposta não é JSON", "resposta_bruta": resposta.text}
                self.metricas['total_requisicoes'] += 1
                self.metricas['requisicoes_sucesso'] += 1
                self.metricas['tempo_total'] += time.time() - inicio
                self.metricas['ultimos_status'].append(getattr(resposta, 'status_code', 'erro'))
                return resultado
            except HTTPError as e:
                status = e.response.status_code if e.response else None
                if status == 429:
                    from src.http_status_reasons import HTTP_STATUS_REASONS
                    reason = e.response.reason if e.response else None
                    error_details = e.response.json().get('error') if e.response and e.response.content else None
                    mensagem_erro = f"Erro na API da OpenAI: {status} - {reason}"
                    if error_details and 'message' in error_details:
                        mensagem_erro += f" Detalhes da API: {error_details['message']}"
                    last_caught_custom_exception = OpenAIRateLimitError(
                        mensagem_erro,
                        status_code=status,
                        error_details=error_details,
                        original_exception=e
                    )
                    logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro HTTP 429. Re-tentando...")
                elif status and status >= 500:
                    from src.http_status_reasons import HTTP_STATUS_REASONS
                    reason = e.response.reason if e.response else None
                    error_details = e.response.json().get('error') if e.response and e.response.content else None
                    mensagem_erro = f"Erro na API da API: {status} - {reason}"
                    if error_details and 'message' in error_details:
                        mensagem_erro += f" Detalhes da API: {error_details['message']}"
                    last_caught_custom_exception = OpenAIServerError(
                        mensagem_erro,
                        status_code=status,
                        error_details=error_details,
                        original_exception=e
                    )
                    logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro HTTP {status}. Re-tentando...")
                elif status in (400, 401, 403, 404):
                    self.metricas['total_requisicoes'] += 1
                    self.metricas['requisicoes_falha'] += 1
                    self.metricas['tempo_total'] += time.time() - inicio
                    self.metricas['ultimos_status'].append(status)
                    self._tratar_erro_resposta(e.response)
                    return  # Interrompe o loop imediatamente para erro 400, 401, 403, 404
                else:
                    if tentativa == self.max_tentativas:
                        self.metricas['total_requisicoes'] += 1
                        self.metricas['requisicoes_falha'] += 1
                        self.metricas['tempo_total'] += time.time() - inicio
                        self.metricas['ultimos_status'].append(status)
                        self._tratar_erro_resposta(e.response)
                        return
            except Timeout as e:
                status = 'timeout'
                last_caught_custom_exception = OpenAITimeoutError("Tempo limite excedido na conexão com a API OpenAI.", original_exception=e)
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Tempo limite. Re-tentando...")
            except ConnectionError as e:
                status = 'connection'
                last_caught_custom_exception = OpenAIConnectionError(f"Erro de conexão para {url_completa}", original_exception=e)
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro de conexão. Re-tentando...")
            except RequestException as e:
                status = 'request'
                last_caught_custom_exception = OpenAIClientError(f"Erro de requisição inesperado para {url_completa}", original_exception=e)
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro de requisição inesperado. Re-tentando...")
            except Exception as e:
                status = 'exception'
                if tentativa == self.max_tentativas:
                    self.metricas['total_requisicoes'] += 1
                    self.metricas['requisicoes_falha'] += 1
                    self.metricas['tempo_total'] += time.time() - inicio
                    self.metricas['ultimos_status'].append(getattr(e, 'status_code', 'erro'))
                last_caught_custom_exception = OpenAIClientError(f"Erro inesperado durante a requisição para {url_completa}", details=str(e), original_exception=e)
                logger.error(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro inesperado. Re-tentando...", exc_info=True)


            # Backoff só para 429/500, Timeout, ConnectionError
            if last_caught_custom_exception and tentativa < self.max_tentativas:
                if status == 429 or (isinstance(last_caught_custom_exception, (OpenAIServerError, OpenAITimeoutError, OpenAIConnectionError))):
                    tempo_espera = self.fator_backoff * (2 ** tentativa)
                    self._backoff_calls.append(tempo_espera)
                    logger.info(f"Aguardando {tempo_espera:.2f} segundos antes da próxima tentativa...")
                    time.sleep(tempo_espera)

            # Se excedeu tentativas para erros retentáveis, levanta OpenAIRetryError
            if tentativa == self.max_tentativas and last_caught_custom_exception:
                if self.max_tentativas == 0:
                    raise last_caught_custom_exception
                # Para 429/500/Timeout/ConnectionError, SEMPRE levanta OpenAIRetryError
                if status == 429 or (isinstance(last_caught_custom_exception, (OpenAIServerError, OpenAITimeoutError, OpenAIConnectionError))):
                    raise OpenAIRetryError(
                        f"Máximo de retries ({self.max_tentativas}) excedido para {url_completa}",
                        original_exception=last_caught_custom_exception
                    )
                else:
                    raise last_caught_custom_exception
        raise OpenAIClientError("Erro desconhecido: A requisição falhou sem exceção capturada e sem retorno de dados.")

# -----------------------------------------------------------------------------
#
# Este módulo implementa o ClienteHttpOpenAI, responsável por toda a comunicação
# HTTP com a API da OpenAI. Centraliza lógica de requisições, tratamento de erros,
# retries, backoff exponencial, rate limiting e coleta de métricas de uso.
#
# Principais pontos:
# - Suporte a GET e POST para endpoints da OpenAI.
# - Implementa retries automáticos com backoff para erros temporários (429, 5xx, timeout, conexão).
# - Rate limiter local para evitar excesso de requisições por segundo.
# - Tratamento detalhado de erros, lançando exceções customizadas para cada tipo de falha.
# - Coleta métricas de uso para monitoramento.
#
# Uso típico:
#   cliente = ClienteHttpOpenAI()
#   resposta = cliente.enviar('chat/completions', dados)
#
# Este arquivo é fundamental para garantir robustez, resiliência e rastreabilidade
# nas integrações com a API da OpenAI, abstraindo detalhes de rede e tratamento de falhas.
# -----------------------------------------------------------------------------