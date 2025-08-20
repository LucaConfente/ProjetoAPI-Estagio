# src/http_client.py

# Gerenciar as requisições HTTP, autenticação com a chave da API
# tratamento de erros customizados pelo outro arquivo de exceções

import requests
import json
import time # Adicionado para o backoff

from src.config import Configuracao # Ajuste para o nome da classe de configuração
from src.exceptions import (
    ErroClienteOpenAI, ErroAutenticacaoOpenAI, ErroRequisicaoInvalidaOpenAI,
    ErroNaoEncontradoOpenAI, ErroLimiteTaxaOpenAI, ErroServidorOpenAI,
    ErroTempoLimiteClienteOpenAI, ErroConexaoOpenAI, ErroTentativaNovamenteOpenAI, ErroAPIOpenAI
)





class ClienteHttpOpenAI:
    def __init__(self):
        self.configuracao = Configuracao.obter_instancia() # Ajuste para o nome da classe de configuração
        self.url_base = self.configuracao.URL_BASE_OPENAI
        self.chave_api = self.configuracao.CHAVE_API_OPENAI
        self.tempo_limite = self.configuracao.TEMPO_LIMITE_OPENAI
        self.max_tentativas = self.configuracao.MAX_TENTATIVAS_OPENAI # Configuração para o máximo de tentativas
        self.fator_backoff = self.configuracao.FATOR_BACKOFF_OPENAI # Configuração para o fator de backoff

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
        detalhes_erro = None

        try:
            json_erro = resposta.json()
            if "error" in json_erro:
                detalhes_erro = json_erro["error"]
                mensagem_erro += f" | Detalhes da API: {detalhes_erro.get('message', 'N/A')}"
        except json.JSONDecodeError:
            mensagem_erro += f" | Corpo da resposta não-JSON: {resposta.text[:200]}..."
        
        if codigo_status in (401, 403):
            raise ErroAutenticacaoOpenAI(mensagem_erro)
        elif codigo_status == 400:
            raise ErroRequisicaoInvalidaOpenAI(mensagem_erro)
        elif codigo_status == 404:
            raise ErroNaoEncontradoOpenAI(mensagem_erro)
        elif codigo_status == 429:
            raise ErroLimiteTaxaOpenAI(mensagem_erro)
        elif codigo_status >= 500:
            raise ErroServidorOpenAI(mensagem_erro)
        else:
            raise ErroAPIOpenAI(mensagem_erro, codigo_status=codigo_status, detalhes_erro=detalhes_erro)

    def _realizar_requisicao(self, metodo: str, ponto_final: str, **kwargs) -> dict:
        """
        Realiza uma requisição HTTP para a API da OpenAI com lógica de retry e backoff.
        """
        url_completa = f"{self.url_base}/{ponto_final}"
        kwargs.setdefault('timeout', self.tempo_limite)
        ultima_excecao = None # Para guardar a última exceção ocorrida

        # O loop tenta fazer a requisição no máximo 'max_tentativas + 1' vezes (a tentativa inicial + max_tentativas retries)
        for tentativa in range(self.max_tentativas + 1):
            try:
                resposta = self.sessao.request(metodo, url_completa, **kwargs)
                resposta.raise_for_status() # Lança um HTTPError para respostas 4xx/5xx

                try:
                    return resposta.json()
                except json.JSONDecodeError:
                    print(f"Aviso: Resposta da API não é JSON para {url_completa}. Conteúdo: {resposta.text[:100]}...")
                    # Retorna a mensagem e a resposta bruta para que o chamador possa lidar com isso
                    return {"mensagem": "Requisição bem-sucedida, mas resposta não é JSON", "resposta_bruta": resposta.text}

            except requests.exceptions.Timeout as e:
                ultima_excecao = ErroTempoLimiteClienteOpenAI(f"Tempo limite excedido na requisição para {url_completa}: {e}")
                print(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Tempo limite. Re-tentando...")

            except requests.exceptions.ConnectionError as e:
                ultima_excecao = ErroConexaoOpenAI(f"Erro de conexão para {url_completa}: {e}")
                print(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro de conexão. Re-tentando...")

            except requests.exceptions.HTTPError as e:
                # HTTPError captura 4xx e 5xx

                # Só tenta retry para 429 (muitas Requests) ou 5xx (Server Errors)
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    ultima_excecao = e # Guarda o erro HTTP original para re-uso
                    print(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro HTTP {e.response.status_code}. Re-tentando...")
                else:
                    # Para outros 4xx (400, 401, 403, 404), não faz retry e levanta a exceção customizada imediatamente
                    self._tratar_erro_resposta(e.response) # Isso levantará a exceção apropriada
            except Exception as e: # Captura outras exceções inesperadas
                ultima_excecao = ErroClienteOpenAI(f"Erro inesperado durante a requisição para {url_completa}: {e}")
                print(f"Tentativa {tentativa + 1}/{self.max_tentativas + 1}: Erro inesperado. Re-tentando...")
            
            # Se ainda houver tentativas restantes
            if tentativa < self.max_tentativas:
                tempo_espera = self.fator_backoff * (2 ** tentativa) # Lógica de backoff exponencial
                print(f"Aguardando {tempo_espera:.2f} segundos antes da próxima tentativa...")
                time.sleep(tempo_espera) # para a execução 
            
        # Se o loop terminar e ainda houver uma exceção pendente
        if ultima_excecao:
            if isinstance(ultima_excecao, requests.exceptions.HTTPError):
                # Se a última exceção foi um HTTPError, use o tratador de erros
                self._tratar_erro_resposta(ultima_excecao.response)
            else:
                # Para outras exceções (Tempo limite, Erro de conexão, etc.), ErroTentativaNovamenteOpenAI
                raise ErroTentativaNovamenteOpenAI(
                    f"Máximo de retries ({self.max_tentativas}) excedido para {url_completa}",
                    excecao_original=ultima_excecao # Passa a exceção original para mais detalhes
                )
        
        # Caso o loop termine sem sucesso e sem uma exceção específica para levantar (cenário improvável)
        raise ErroClienteOpenAI(f"Requisição para {url_completa} falhou por motivo desconhecido após os retries.")

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
