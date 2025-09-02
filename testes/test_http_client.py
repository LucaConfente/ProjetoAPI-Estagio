import requests
import pytest
import requests.exceptions as req_exc 
import requests_mock
import json
import sys
import os
import logging # Importa o módulo de logging para desativar durante os testes

from requests.exceptions import Timeout, RequestException, HTTPError


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importa as classes do nosso projeto, já com os nomes em inglês, conforme o que o Python está lendo
from src.http_client import ClienteHttpOpenAI
from src.config import Config # ALTERADO: Usando a classe Config refatorada
from src.exceptions import (
    OpenAIClientError, OpenAIAuthenticationError, OpenAIBadRequestError,
    OpenAINotFoundError, OpenAIRateLimitError, OpenAIServerError,
    OpenAITimeoutError, OpenAIConnectionError, OpenAIRetryError, OpenAIAPIError
)

logging.disable(logging.CRITICAL)
print(logging.getLogger().handlers)

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

    config_instancia.OPENAI_API_KEY = "sk-test1234567890abcdefghijklmnopqrstuvwxyz" # Chave API válida (formato)
    config_instancia.OPENAI_BASE_URL = "https://api.openai.com/v1"
    config_instancia.OPENAI_TIMEOUT = 10
    config_instancia.OPENAI_MAX_RETRIES = 2 # Define 0 tentativas para a maioria dos testes de erro único
    config_instancia.OPENAI_BACKOFF_FACTOR = 0.01 # Fator pequeno para retries rápidos

    yield # Os testes que usam esta fixture serão executados aqui
    
    # Restaura os valores originais da Configuração após os testes
    for atributo, valor in valores_originais.items():
        setattr(config_instancia, atributo, valor)



# Fixture para criar uma instância do ClienteHttpOpenAI para cada teste.
# Depende da fixture 'configurar_cliente_para_teste' para garantir que as configurações estejam prontas.
@pytest.fixture
def cliente_http(configurar_cliente_para_teste):
    return ClienteHttpOpenAI()




def test_inicializacao_cliente_http(cliente_http):
    """Testa se o cliente HTTP inicializa corretamente com as configurações."""
    assert cliente_http.url_base == "https://api.openai.com/v1"
    assert cliente_http.chave_api.startswith("sk-")
    assert cliente_http.tempo_limite == 10
  
    assert isinstance(cliente_http.sessao, requests.Session) 
    assert cliente_http.max_tentativas == 2
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
    cliente_http.max_tentativas = 1
    cliente_http.fator_backoff = 0.001
    ponto_final_teste = "rate_limit_endpoint"

    response_429 = requests.Response()
    response_429.status_code = 429
    response_429._content = b'{"error": {"message": "Limite de taxa excedido", "type": "rate_limit_error"}}'
    response_429.reason = "Too Many Requests"

    # Mocka duas tentativas, ambas levantando HTTPError
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=HTTPError(response=response_429))
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=HTTPError(response=response_429))

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.obter(ponto_final_teste)

    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, HTTPError)
    assert info_excecao.value.original_exception.response.status_code == 429
    assert requests_mock.call_count == 2 # Deve ter feito 2 chamadas (original + 1 retry)




def test_erro_http_resposta_500_com_retries(cliente_http, requests_mock):
    """Testa o tratamento de erro HTTP (ex: 500 Erro Interno do Servidor) com retries."""
    from requests.exceptions import HTTPError
    cliente_http.max_tentativas = 1
    cliente_http.fator_backoff = 0.001
    ponto_final_teste = "server_error_endpoint"

    response_500 = requests.Response()
    response_500.status_code = 500
    response_500._content = b'{"error": {"message": "Erro interno do servidor", "type": "server_error"}}'
    response_500.reason = "Internal Server Error"

    # Mocka duas tentativas, ambas levantando HTTPError
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", exc=HTTPError(response=response_500))
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", exc=HTTPError(response=response_500))

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.enviar(ponto_final_teste, dados={})

    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, HTTPError)
    assert info_excecao.value.original_exception.response.status_code == 500
    assert requests_mock.call_count == 2




def test_excecao_tempo_limite_com_retries(cliente_http, requests_mock):
    """Testa se uma exceção de Tempo Limite é levantada corretamente após retries."""
    cliente_http.max_tentativas = 1 # Define 1 tentativa de retry
    cliente_http.fator_backoff = 0.001 # Fator pequeno para teste rápido

    ponto_final_teste = "slow_endpoint"
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=req_exc.Timeout) # Primeira tentativa: timeout
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=req_exc.Timeout) # Segunda tentativa: timeout também

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.obter(ponto_final_teste)

    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    # CORREÇÃO AQUI: Apenas um nível de original_exception
    assert isinstance(info_excecao.value.original_exception, OpenAITimeoutError)
    # Opcional: Para verificar a exceção original do requests
    assert isinstance(info_excecao.value.original_exception.original_exception, req_exc.Timeout)


def test_excecao_conexao_com_retries(cliente_http, requests_mock):
    """Testa se uma exceção de conexão é levantada corretamente após retries."""
    cliente_http.max_tentativas = 1 # Define 1 tentativa de retry
    cliente_http.fator_backoff = 0.001

    ponto_final_teste = "network_issue"
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=req_exc.ConnectionError("Problema de rede"))
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=req_exc.ConnectionError("Problema de rede"))

    with pytest.raises(OpenAIRetryError) as info_excecao:
        cliente_http.obter(ponto_final_teste)

    assert "Máximo de retries (1) excedido" in str(info_excecao.value)
    # CORREÇÃO AQUI: Apenas um nível de original_exception
    assert isinstance(info_excecao.value.original_exception, OpenAIConnectionError)
    # Opcional: Para verificar a exceção original do requests
    assert isinstance(info_excecao.value.original_exception.original_exception, req_exc.ConnectionError)
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
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=requests.exceptions.ConnectionError("Problema de rede"))

    with pytest.raises(OpenAIConnectionError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    assert "Erro de conexão para" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, requests.exceptions.ConnectionError)
    assert requests_mock.call_count == 1


def test_excecao_request_generica_sem_retries(cliente_http, requests_mock):
    """Testa se uma exceção Requests genérica é levantada corretamente SEM retries.
    Deve levantar OpenAIConnectionError.
    """
    cliente_http.max_tentativas = 0
    ponto_final_teste = "generic_request_error"
    
    # Use uma RequestException genérica, que não é Timeout ou ConnectionError
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", exc=RequestException("Erro desconhecido da requisição HTTP"))

    with pytest.raises(OpenAIClientError) as info_excecao: 
        cliente_http.obter(ponto_final_teste)
    assert "Erro de requisição inesperado para" in str(info_excecao.value)
    assert isinstance(info_excecao.value.original_exception, RequestException)
    assert requests_mock.call_count == 1


# ...

def test_erro_http_resposta_generica_api(cliente_http, requests_mock):
    """Testa o tratamento de um erro HTTP genérico da API (ex: 403 Forbidden)."""
    ponto_final_teste = "forbidden_endpoint"
    mensagem_erro_api = {"error": {"message": "Acesso negado", "type": "permission_error"}}
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=mensagem_erro_api, status_code=403) 

    # O método _tratar_erro_resposta levanta especificamente OpenAIAuthenticationError para 403
    with pytest.raises(OpenAIAuthenticationError) as info_excecao:
        cliente_http.obter(ponto_final_teste)
    
    # Mensagem correta agora é "403 - Forbidden"
    assert "403 - Forbidden" in str(info_excecao.value)
    assert "Acesso negado" in str(info_excecao.value)


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
    requests_mock.post(f"{cliente_http.url_base}/{ponto_final_teste}", json=resposta_mock, status_code=200)
    resposta = cliente_http.enviar(ponto_final_teste, dados=None)
    assert resposta == resposta_mock
    assert requests_mock.last_request.text in (None, "")  # Aceita ambos
    assert requests_mock.call_count == 2


def test_retry_backoff_exponencial(cliente_http, requests_mock):
    """
    Testa se o retry com backoff exponencial é executado corretamente para erros temporários (HTTP 500).
    O tempo de espera entre tentativas deve dobrar a cada retry.
    """
    import time
    ponto_final_teste = "test_retry"
    # Simula duas falhas 500 e uma resposta 200 na terceira tentativa
    responses = [
        {'status_code': 500, 'json': {'error': {'message': 'Erro temporário'}}},
        {'status_code': 500, 'json': {'error': {'message': 'Erro temporário'}}},
        {'status_code': 200, 'json': {'result': 'ok'}}
    ]
    chamada = {'count': 0}
    def responder(request, context):
        idx = chamada['count']
        chamada['count'] += 1
        context.status_code = responses[idx]['status_code']
        return responses[idx]['json']
    requests_mock.get(f"{cliente_http.url_base}/{ponto_final_teste}", json=responder)

    # Patch time.sleep para capturar os tempos de espera
    sleep_calls = []
    original_sleep = time.sleep
    def fake_sleep(seconds):
        sleep_calls.append(seconds)
    time.sleep = fake_sleep

    try:
        resposta = cliente_http.obter(ponto_final_teste)
        assert resposta == {'result': 'ok'}
        # Espera: [fator_backoff * 2^0, fator_backoff * 2^1] = [0.01, 0.02] (valores padrão)
        assert sleep_calls == [cliente_http.fator_backoff * (2 ** i) for i in range(2)]
    finally:
        time.sleep = original_sleep


def test_rate_limiter_temporiza_requisicoes():
    """
    Testa se o rate limiter do ClienteHttpOpenAI limita o número de requisições por segundo.
    Faz 5 requisições com limite de 2/s e mede o tempo total.
    """
    import time
    from src.http_client import ClienteHttpOpenAI

    cliente = ClienteHttpOpenAI(max_requisicoes_por_segundo=2.0)

    # Mocka o método de requisição para não depender da API real
    class FakeResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"ok": True}

    def fake_request(*args, **kwargs):
        return FakeResponse()

    cliente.sessao.request = fake_request

    inicio = time.time()
    for _ in range(5):
        cliente._realizar_requisicao("GET", "models")
    fim = time.time()
    tempo_total = fim - inicio

    # 2 requisições instantâneas, 3 limitadas (cada espera 0.5s): tempo mínimo esperado = 1.5s
    assert tempo_total >= 1.5, f"Rate limiter não atrasou o suficiente: {tempo_total:.2f}s"


def test_metricas_de_uso_registram_sucesso_e_falha():
    """
    Testa se as métricas de uso do ClienteHttpOpenAI registram corretamente sucessos e falhas.
    """
    from src.http_client import ClienteHttpOpenAI
    import time

    cliente = ClienteHttpOpenAI()

    # Mocka o método de requisição para simular sucesso e falha
    class FakeResponse:
        def __init__(self, status_code=200):
            self.status_code = status_code
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception('Erro', self)
        def json(self):
            return {"ok": True}

    def fake_request_sucesso(*args, **kwargs):
        return FakeResponse(200)
    def fake_request_falha(*args, **kwargs):
        return FakeResponse(500)

    cliente.sessao.request = fake_request_sucesso
    cliente._realizar_requisicao("GET", "models")
    cliente.sessao.request = fake_request_falha
    try:
        cliente._realizar_requisicao("GET", "models")
    except Exception:
        pass

    metricas = cliente.get_metricas()
    assert metricas['total_requisicoes'] == 2
    assert metricas['requisicoes_sucesso'] == 1
    assert metricas['requisicoes_falha'] == 1
    assert len(metricas['ultimos_status']) == 2
    assert metricas['ultimos_status'][0] == 200
    assert metricas['ultimos_status'][1] == 500 or metricas['ultimos_status'][1] == 'erro'
