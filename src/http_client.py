
import requests
import json
import time
import logging # Importa o módulo de logging

# Importa a classe de configuração refatorada
from src.config import Config 
# Importa as exceções customizadas
from src.exceptions import (
    OpenAIClientError, OpenAIAuthenticationError, OpenAIBadRequestError,
    OpenAINotFoundError, OpenAIRateLimitError, OpenAIServerError,
    OpenAITimeoutError, OpenAIConnectionError, OpenAIRetryError, OpenAIAPIError
)

# Configura o logger para este módulo
logger = logging.getLogger(__name__)


class ClienteHttpOpenAI:
    def __init__(self):
        # Ajuste para usar a classe Config e seu método get_instance()
        self.configuracao = Config.get_instance() 
        
        # Ajuste para os novos nomes dos atributos da classe Config
        self.url_base = self.configuracao.OPENAI_BASE_URL
        self.chave_api = self.configuracao.OPENAI_API_KEY
        self.tempo_limite = self.configuracao.OPENAI_TIMEOUT
        self.max_tentativas = self.configuracao.OPENAI_MAX_RETRIES
        self.fator_backoff = self.configuracao.OPENAI_BACKOFF_FACTOR

        self.sessao = requests.Session()
        self.sessao.headers.update({
            "Authorization": f"Bearer {self.chave_api}",
            "Content-Type": "application/json"
        })

    def _tratar_erro_resposta(self, resposta: requests.Response):
        """
        Trata as respostas de erro da API e levanta exceções customizadas.
        """
        codigo_status = resposta.status_code
        mensagem_erro = f"Erro na API da OpenAI: {codigo_status} - {resposta.reason}"
        error_details = None # Renomeado para consistência com as exceções

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
            # Passando error_details para o parâmetro correto da exceção
            raise OpenAIAPIError(mensagem_erro, status_code=codigo_status, error_details=error_details)

    def _realizar_requisicao(self, metodo: str, ponto_final: str, **kwargs) -> dict:
        """
        Realiza uma requisição HTTP para a API da OpenAI com lógica de retry e backoff.
        """
        url_completa = f"{self.url_base}/{ponto_final}"
        kwargs.setdefault('timeout', self.tempo_limite)
        ultima_excecao = None

        for tentativa in range(self.max_tentativas + 1):
            try:
                resposta = self.sessao.request(metodo, url_completa, **kwargs)
                resposta.raise_for_status()

                try:
                    return resposta.json()
                except json.JSONDecodeError:
                    # Usando logger.warning em vez de print
                    logger.warning(f"Resposta da API não é JSON para {url_completa}. Conteúdo: {resposta.text[:100]}...")
                    return {"mensagem": "Requisição bem-sucedida, mas resposta não é JSON", "resposta_bruta": resposta.text}

            except requests.exceptions.Timeout as e:
                ultima_excecao = OpenAITimeoutError(f"Tempo limite excedido na requisição para {url_completa}", original_exception=e)
                # Usando logger.warning em vez de print
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Tempo limite. Re-tentando...")

            except requests.exceptions.ConnectionError as e:
                ultima_excecao = OpenAIConnectionError(f"Erro de conexão para {url_completa}", original_exception=e)
                # Usando logger.warning em vez de print
                logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro de conexão. Re-tentando...")

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    ultima_excecao = e
                    # Usando logger.warning em vez de print
                    logger.warning(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro HTTP {e.response.status_code}. Re-tentando...")
                else:
                    # Para outros 4xx, não faz retry e levanta a exceção customizada imediatamente
                    self._tratar_erro_resposta(e.response)
            except Exception as e:
                ultima_excecao = OpenAIClientError(f"Erro inesperado durante a requisição para {url_completa}", details=str(e))
                # Usando logger.error em vez de print
                logger.error(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro inesperado. Re-tentando...", exc_info=True)
            
            if tentativa < self.max_tentativas:
                tempo_espera = self.fator_backoff * (2 ** tentativa)
                # Usando logger.info em vez de print
                logger.info(f"Aguardando {tempo_espera:.2f} segundos antes da próxima tentativa...")
                time.sleep(tempo_espera)
            
        if ultima_excecao:
            if isinstance(ultima_excecao, requests.exceptions.HTTPError):
                self._tratar_erro_resposta(ultima_excecao.response)
            else:
                raise OpenAIRetryError(
                    f"Máximo de retries ({self.max_tentativas}) excedido para {url_completa}",
                    original_exception=ultima_excecao
                )
        
        raise OpenAIClientError(f"Requisição para {url_completa} falhou por motivo desconhecido após os retries.")

    def obter(self, ponto_final: str, parametros: dict = None) -> dict:
        """
        Realiza uma requisição GET para a API da OpenAI.
        """
        return self._realizar_requisicao("GET", ponto_final, params=parametros)

    def enviar(self, ponto_final: str, dados: dict = None) -> dict:
        """
        Realiza uma requisição POST para a API da OpenAI.
        """
        return self._realizar_requisicao("POST", ponto_final, json=dados)
