
import requests
import pytest
import requests_mock
import json
import sys
import os
import logging # Importa o módulo de logging para desativar durante os testes

# Importa as classes de exceção do módulo requests para mocking
from requests.exceptions import Timeout, RequestException

# Adiciona o diretório raiz do projeto ao sys.path
# Caminha dois níveis acima do diretório atual (tests/core_library -> tests -> Raiz_do_Projeto)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importa as classes do nosso projeto, já com os nomes em inglês, conforme o que o Python está lendo
from src.http_client import ClienteHttpOpenAI
from src.config import Config # ALTERADO: Usando a classe Config refatorada
from src.exceptions import (
    OpenAIClientError, OpenAIAuthenticationError, OpenAIBadRequestError,
    OpenAINotFoundError, OpenAIRateLimitError, OpenAIServerError,
    OpenAITimeoutError, OpenAIConnectionError, OpenAIRetryError, OpenAIAPIError
)

# Desativa o logging durante os testes para evitar poluir a saída do pytest
# As mensagens de log ainda podem ser capturadas pela fixture caplog se necessário
logging.disable(logging.CRITICAL)

# Fixture para garantir que temos uma configuração válida para o cliente durante os testes.
# O escopo 'module' significa que esta fixture será executada apenas uma vez por módulo de teste.
@pytest.fixture(scope="module")
def configurar_cliente_para_teste():
    """
    Configura a instância de Config para os testes, garantindo que
    o ClienteHttpOpenAI possa inicializar sem erros de chave API ou outras configs.
    Define valores dummy e restaura os originais após os testes.
    """
    # ALTERADO: Obtém a instância singleton da Config
    config_instancia = Config.get_instance()
    
    # Guarda os valores originais para restaurar após os testes
    valores_originais = {
        'OPENAI_API_KEY': config_instancia.OPENAI_API_KEY,
        'OPENAI_BASE_URL': config_instancia.OPENAI_BASE_URL,
        'OPENAI_TIMEOUT': config_instancia.OPENAI_TIMEOUT,
        'OPENAI_MAX_RETRIES': config_instancia.OPENAI_MAX_RETRIES,
        'OPENAI_BACKOFF_FACTOR': config_instancia.OPENAI_BACKOFF_FACTOR,
    }

    # Define valores dummy para o teste
    # ALTERADO: Usando os novos nomes de atributos da classe Config
    config_instancia.OPENAI_API_KEY = "sk-test1234567890abcdefghijklmnopqrstuvwxyz" # Chave API válida (formato)
    config_instancia.OPENAI_BASE_URL = "https://api.openai.com/v1"
    config_instancia.OPENAI_TIMEOUT = 10
    config_instancia.OPENAI_MAX_RETRIES = 0 # Define 0 tentativas para a maioria dos testes de erro único
    config_instancia.OPENAI_BACKOFF_FACTOR = 0.01 # Fator pequeno para retries rápidos

    yield # Os testes que usam esta fixture serão executados aqui
    
    # Restaura os valores originais da Configuração após os testes
    for atributo, valor in valores_originais.items():
        setattr(config_instancia, atributo, valor)


# Fixture para criar uma instância do ClienteHttpOpenAI para cada teste.
# Depende da fixture 'configurar_cliente_para_teste' para garantir que as configurações estejam prontas.
@pytest.fixture
def cliente_http(configurar_cliente_para_teste):
    """
    Fornece uma nova instância de ClienteHttpOpenAI para cada teste,
    garantindo o isolamento entre os testes.
    """
    return ClienteHttpOpenAI()


def test_inicializacao_cliente_http(cliente_http):
    """Testa se o cliente HTTP inicializa corretamente com as configurações."""
    assert cliente_http.url_base == "https://api.openai.com/v1"
    assert cliente_http.chave_api.startswith("sk-")
    assert cliente_http.tempo_limite == 10
    # requests_mock.requests.Session é o tipo real da sessão, mesmo quando mockado.
    assert isinstance(cliente_http.sessao, requests_mock.requests.Session) 
    assert cliente_http.max_tentativas == 0 # Verifica o valor configurado pela fixture
    assert cliente_http.fator_backoff == 0.01 # Verifica o valor configurado pela fixture


def test_resposta_get_sucesso(cliente_http, requests_mock):
    """Testa uma requisição GET bem-sucedida."""
    ponto_final_teste = "models"
    resposta_mock = {"data": [{"id": "gpt-3.5-turbo"}], "object": "list"}
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=resposta_mock, status_code=200)

    resposta = cliente_http.obter(ponto_final_teste) # Usa o método traduzido 'obter'
    assert resposta == resposta_mock
    assert requests_mock.call_count == 1 # Verifica que apenas uma chamada foi feita


def test_resposta_post_sucesso(cliente_http, requests_mock):
    """Testa uma requisição POST bem-sucedida."""
    ponto_final_teste = "chat/completions"
    dados_teste = {"messages": [{"role": "user", "content": "Olá"}]}
    resposta_mock = {"id": "chatcmpl-123", "choices": [], "object": "chat.completion"}
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=resposta_mock, status_code=200)

    resposta = cliente_http.enviar(ponto_final_teste, dados=dados_teste) # Usa o método traduzido 'enviar'
    assert resposta == resposta_mock
    assert requests_mock.called_once # Verifica que apenas uma chamada foi feita
    # Verifica se os cabeçalhos padrão foram enviados
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {cliente_http.chave_api}"
    assert requests_mock.last_request.headers["Content-Type"] == "application/json"


def test_erro_http_resposta_400(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 400 Requisição Inválida)"""
    ponto_final_teste = "bad_request_endpoint"
    mensagem_erro_api = {"error": {"message": "Parâmetro inválido", "type": "invalid_request_error"}}
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=400)

    with pytest.raises(OpenAIBadRequestError) as info_excecao:
        cliente_http.enviar(ponto_final_teste, dados={})
    
    assert "400 - Bad Request" in str(info_excecao.value)
    assert "Detalhes da API: Parâmetro inválido" in str(info_excecao.value)


def test_erro_http_resposta_401(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 401 Não Autorizado)"""
    ponto_final_teste = "unauthorized_endpoint"
    mensagem_erro_api = {"error": {"message": "Chave API incorreta", "type": "authentication_error"}}
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=401)

    with pytest.raises(OpenAIAuthenticationError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "401 - Unauthorized" in str(info_excecao.value)
    assert "Detalhes da API: Chave API incorreta" in str(info_excecao.value)


def test_erro_http_resposta_404(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 404 Não Encontrado)."""
    ponto_final_teste = "non_existent_endpoint"
    mensagem_erro_api = {"error": {"message": "Recurso não encontrado", "type": "invalid_request_error"}}
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=404)

    with pytest.raises(OpenAINotFoundError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "404 - Not Found" in str(info_excecao.value)
    assert "Detalhes da API: Recurso não encontrado" in str(info_excecao.value)


def test_erro_http_resposta_429_com_retries(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 429 Too Many Requests) com retries."""
    cliente_http.max_tentativas = 1 # Define 1 tentativa de retry
    cliente_http.fator_backoff = 0.001 # Fator pequeno para teste rápido

    ponto_final_teste = "rate_limit_endpoint"
    mensagem_erro_api = {"error": {"message": "Limite de taxa excedido", "type": "rate_limit_error"}}
    
    # Mocka duas respostas 429: a primeira tentativa e a tentativa de retry
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=429)
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=429)

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    # Verifica se a exceção original encapsulada é um HTTPError da resposta 429
    assert isinstance(info_excecao.value.original_exception, requests_mock.requests.exceptions.HTTPError)
    assert info_excecao.value.original_exception.response.status_code == 429
    assert requests_mock.call_count == 2 # Deve ter feito 2 chamadas (original + 1 retry)


def test_erro_http_resposta_500_com_retries(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 500 Erro Interno do Servidor) com retries."""
    cliente_http.max_tentativas = 1 # Define 1 tentativa de retry
    cliente_http.fator_backoff = 0.001 # Fator pequeno para teste rápido

    ponto_final_teste = "server_error_endpoint"
    mensagem_erro_api = {"error": {"message": "Erro interno do servidor", "type": "server_error"}}
    
    # Mocka duas respostas 500
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=500)
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=500)


    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.enviar(ponto_final_teste, dados={})
    
    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, requests_mock.requests.exceptions.HTTPError)
    assert info_excecao.value.original_exception.response.status_code == 500
    assert requests_mock.call_count == 2 # Deve ter feito 2 chamadas (original + 1 retry)


def test_excecao_tempo_limite_com_retries(cliente_http, requests_mock):
    """Testa se uma exceção de Tempo Limite é levantada corretamente após retries."""
    cliente_http.max_tentativas = 1 # Define 1 tentativa de retry
    cliente_http.fator_backoff = 0.001

    ponto_final_teste = "slow_endpoint"
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=Timeout) # Primeira tentativa: timeout
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=Timeout) # Segunda tentativa: timeout também

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, Timeout)
    assert requests_mock.call_count == 2 # Deve ter feito 2 chamadas


def test_excecao_conexao_com_retries(cliente_http, requests_mock):
    """Testa se uma exceção de conexão é levantada corretamente após retries."""
    cliente_http.max_tentativas = 1 # Define 1 tentativa de retry
    cliente_http.fator_backoff = 0.001

    ponto_final_teste = "network_issue"
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=requests_mock.requests.exceptions.ConnectionError("Problema de rede"))
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=requests_mock.requests.exceptions.ConnectionError("Problema de rede"))

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, requests_mock.requests.exceptions.ConnectionError)
    assert requests_mock.call_count == 2 # Deve ter feito 2 chamadas


def test_resposta_nao_json(cliente_http, requests_mock):
    """Testa a requisição quando a resposta não é um JSON válido."""
    ponto_final_teste = "plain_text"
    resposta_texto_simples = "OK - Isto é texto simples, não JSON."
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", text=resposta_texto_simples, status_code=200)

    resposta = cliente_http.obter(ponto_final_teste)
    assert "Requisição bem-sucedida, mas resposta não é JSON" in resposta["mensagem"]
    assert resposta["resposta_bruta"].startswith("OK - Isto é texto simples, não JSON.")
    assert requests_mock.call_count == 1


# Teste para verificar o caso em que um retry é bem-sucedido
def test_retry_bem_sucedido(cliente_http, requests_mock):
    """Testa se o cliente tenta novamente após uma falha e tem sucesso na próxima tentativa."""
    cliente_http.max_tentativas = 2 # Permite até 2 retries
    cliente_http.fator_backoff = 0.001 # Fator pequeno para teste rápido

    ponto_final_teste = "flaky_endpoint"
    resposta_sucesso = {"status": "ok", "message": "Sucesso após retry!"}

    # Define o comportamento do mock:
    # 1. Primeira chamada: Falha com 500
    # 2. Segunda chamada (primeiro retry): Sucesso com 200
    # (requests_mock automaticamente avança para a próxima definição de mock na mesma URL)
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", [
        {'json': {"error": {"message": "Erro de servidor", "type": "server_error"}}, 'status_code': 500},
        {'json': resposta_sucesso, 'status_code': 200}
    ])

    resposta = cliente_http.obter(ponto_final_teste)
    assert resposta == resposta_sucesso
    assert requests_mock.call_count == 2 # Deve ter feito 2 chamadas (a original que falhou + 1 retry que obteve sucesso)


# --- NOVOS TESTES IMPLEMENTADOS ---

def test_erro_http_resposta_500_sem_retries(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 500 Erro Interno do Servidor) SEM retries.
    Deve levantar OpenAIServerError diretamente.
    """
    cliente_http.max_tentativas = 0 # Assegura que não haverá retries (já é o default da fixture, mas bom explicitar)
    ponto_final_teste = "server_error_endpoint_no_retry"
    mensagem_erro_api = {"error": {"message": "Erro interno do servidor", "type": "server_error"}}
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=500)

    with pytest.raises(OpenAIServerError) as info_excecao:
        cliente_http.enviar(ponto_final_teste, dados={})
    
    assert "500 - Internal Server Error" in str(info_excecao.value)
    assert "Detalhes da API: Erro interno do servidor" in str(info_excecao.value)
    assert requests_mock.call_count == 1


def test_erro_http_resposta_429_sem_retries(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 429 Too Many Requests) SEM retries.
    Deve levantar OpenAIRateLimitError diretamente.
    """
    cliente_http.max_tentativas = 0 # Assegura que não haverá retries
    ponto_final_teste = "rate_limit_endpoint_no_retry"
    mensagem_erro_api = {"error": {"message": "Limite de taxa excedido", "type": "rate_limit_error"}}
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=429)

    with pytest.raises(OpenAIRateLimitError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "429 - Too Many Requests" in str(info_excecao.value)
    assert "Detalhes da API: Limite de taxa excedido" in str(info_excecao.value)
    assert requests_mock.call_count == 1


def test_excecao_tempo_limite_sem_retries(cliente_http, requests_mock):
    """Testa se uma exceção de Tempo Limite é levantada corretamente SEM retries.
    Deve levantar OpenAITimeoutError diretamente.
    """
    cliente_http.max_tentativas = 0
    ponto_final_teste = "slow_endpoint_no_retry"
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=Timeout)

    with pytest.raises(OpenAITimeoutError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "Tempo limite excedido na conexão com a API OpenAI." in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, Timeout)
    assert requests_mock.call_count == 1


def test_excecao_conexao_sem_retries(cliente_http, requests_mock):
    """Testa se uma exceção de conexão é levantada corretamente SEM retries.
    Deve levantar OpenAIConnectionError diretamente.
    """
    cliente_http.max_tentativas = 0
    ponto_final_teste = "network_issue_no_retry"
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=requests_mock.requests.exceptions.ConnectionError("Problema de rede"))

    with pytest.raises(OpenAIConnectionError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "Problema de conexão de rede com a API OpenAI." in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, requests_mock.requests.exceptions.ConnectionError)
    assert requests_mock.call_count == 1


def test_excecao_request_generica_sem_retries(cliente_http, requests_mock):
    """Testa se uma exceção Requests genérica é levantada corretamente SEM retries.
    Deve levantar OpenAIConnectionError.
    """
    cliente_http.max_tentativas = 0
    ponto_final_teste = "generic_request_error"
    
    # Use uma RequestException genérica, que não é Timeout ou ConnectionError
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=RequestException("Erro desconhecido da requisição HTTP"))

    with pytest.raises(OpenAIConnectionError) as info_excecao: 
        cliente_http.obter(ponto_final_teste)
    
    assert "Problema de conexão de rede com a API OpenAI." in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, RequestException)
    assert requests_mock.call_count == 1


def test_erro_http_resposta_generica_api(cliente_http, requests_mock):
    """Testa o tratamento de um erro HTTP genérico da API (ex: 403 Forbidden).
    Deve levantar OpenAIAPIError.
    """
    ponto_final_teste = "forbidden_endpoint"
    mensagem_erro_api = {"error": {"message": "Acesso negado", "type": "permission_error"}}
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=403)

    with pytest.raises(OpenAIAPIError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "403 - Forbidden" in str(info_excecao.value)
    assert "Detalhes da API: Acesso negado" in str(info_excecao.value)
    assert requests_mock.call_count == 1


def test_erro_http_resposta_400_nao_json(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 400) com resposta NÃO-JSON.
    Verifica se a exceção é levantada e a mensagem é apropriada.
    """
    ponto_final_teste = "bad_request_non_json"
    resposta_texto_simples = "Bad Request: Invalid input from upstream"
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", text=resposta_texto_simples, status_code=400)

    with pytest.raises(OpenAIBadRequestError) as info_excecao:
        cliente_http.enviar(ponto_final_teste, dados={})
    
    assert "400 - Bad Request" in str(info_excecao.value)
    # A mensagem de erro agora inclui o texto bruto da resposta para não-JSON
    assert f"Corpo da resposta não-JSON: {resposta_texto_simples[:200]}..." in str(info_excecao.value)
    assert requests_mock.call_count == 1


def test_post_com_dados_vazios(cliente_http, requests_mock):
    """Testa uma requisição POST com dados vazios (dicionário vazio e None)."""
    ponto_final_teste = "empty_data_post"
    resposta_mock = {"status": "success", "received_data": {}}

    # Cenário 1: dados={} (envia um JSON vazio {})
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=resposta_mock, status_code=200)
    resposta = cliente_http.enviar(ponto_final_teste, dados={})
    assert resposta == resposta_mock
    assert requests_mock.last_request.json() == {} # Deve enviar um objeto JSON vazio
    assert requests_mock.call_count == 1

    # Cenário 2: dados=None (não envia corpo JSON)
    # Re-mocka a URL para a segunda chamada
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=resposta_mock, status_code=200)
    resposta = cliente_http.enviar(ponto_final_teste, dados=None)
    assert resposta == resposta_mock
    # requests_mock.last_request.json() pode ser None ou levantar erro se o corpo for vazio.
    # requests_mock.last_request.text deve ser uma string vazia para json=None.
    assert requests_mock.last_request.text == "" 
    assert requests_mock.call_count == 2
