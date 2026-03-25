"""
test_http_client.py
===================
Testes unitários para o ClienteHttpOpenAI.

Cobre:
- Inicialização do cliente
- Requisições GET e POST bem-sucedidas
- Tratamento de erros HTTP (400, 401, 403, 404, 429, 500)
- Retry com backoff exponencial
- Rate limiter
- Métricas de uso
- Respostas não-JSON
- Casos extremos (dados vazios, erros genéricos)
"""

import sys
import os
import json
import time
import logging

import pytest
import requests
import requests.exceptions as req_exc
import requests_mock
from requests.exceptions import Timeout, RequestException, HTTPError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.http_client import ClienteHttpOpenAI
from src.config import Config
from src.exceptions import (
    OpenAIClientError,
    OpenAIAuthenticationError,
    OpenAIBadRequestError,
    OpenAINotFoundError,
    OpenAIRateLimitError,
    OpenAIServerError,
    OpenAITimeoutError,
    OpenAIConnectionError,
    OpenAIRetryError,
    OpenAIAPIError,
)

# Suprime logs durante os testes
logging.disable(logging.CRITICAL)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def configurar_cliente_para_teste():
    """
    Configura a instância singleton de Config com valores dummy para os testes.
    Restaura os valores originais após a execução do módulo.
    """
    config = Config.get_instance()

    originais = {
        'OPENAI_API_KEY': config.OPENAI_API_KEY,
        'OPENAI_BASE_URL': config.OPENAI_BASE_URL,
        'OPENAI_TIMEOUT': config.OPENAI_TIMEOUT,
        'OPENAI_MAX_RETRIES': config.OPENAI_MAX_RETRIES,
        'OPENAI_BACKOFF_FACTOR': config.OPENAI_BACKOFF_FACTOR,
    }

    config.OPENAI_API_KEY = "sk-test1234567890abcdefghijklmnopqrstuvwxyz"
    config.OPENAI_BASE_URL = "https://api.openai.com/v1"
    config.OPENAI_TIMEOUT = 10
    config.OPENAI_MAX_RETRIES = 2
    config.OPENAI_BACKOFF_FACTOR = 0.01

    yield

    for atributo, valor in originais.items():
        setattr(config, atributo, valor)


@pytest.fixture
def cliente_http(configurar_cliente_para_teste):
    """Instância limpa do ClienteHttpOpenAI para cada teste."""
    return ClienteHttpOpenAI()


# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

class TestInicializacao:

    def test_inicializacao_correta(self, cliente_http):
        """Testa se o cliente inicializa corretamente com as configurações da fixture."""
        assert cliente_http.url_base == "https://api.openai.com/v1"
        assert cliente_http.chave_api.startswith("sk-")
        assert cliente_http.tempo_limite == 10
        assert cliente_http.max_tentativas == 2
        assert cliente_http.fator_backoff == 0.01
        assert isinstance(cliente_http.sessao, requests.Session)


# =============================================================================
# REQUISIÇÕES BEM-SUCEDIDAS
# =============================================================================

class TestRequisicoesSucesso:

    def test_get_sucesso(self, cliente_http, requests_mock):
        """Testa uma requisição GET bem-sucedida."""
        resposta_mock = {"data": [{"id": "gpt-3.5-turbo"}], "object": "list"}
        requests_mock.get(f"{cliente_http.url_base}/models", json=resposta_mock, status_code=200)

        resposta = cliente_http.obter("models")

        assert resposta == resposta_mock
        assert requests_mock.call_count == 1

    def test_post_sucesso(self, cliente_http, requests_mock):
        """Testa uma requisição POST bem-sucedida e verifica os headers."""
        dados = {"messages": [{"role": "user", "content": "Olá"}]}
        resposta_mock = {"id": "chatcmpl-123", "choices": [], "object": "chat.completion"}
        requests_mock.post(f"{cliente_http.url_base}/chat/completions", json=resposta_mock, status_code=200)

        resposta = cliente_http.enviar("chat/completions", dados=dados)

        assert resposta == resposta_mock
        assert requests_mock.last_request.headers["Authorization"] == f"Bearer {cliente_http.chave_api}"
        assert requests_mock.last_request.headers["Content-Type"] == "application/json"

    def test_post_dados_vazios(self, cliente_http, requests_mock):
        """Testa POST com dados={} (deve enviar JSON vazio) e dados=None (sem corpo)."""
        resposta_mock = {"status": "success"}
        requests_mock.post(f"{cliente_http.url_base}/empty", json=resposta_mock, status_code=200)

        # dados={}
        resposta = cliente_http.enviar("empty", dados={})
        assert resposta == resposta_mock
        assert requests_mock.last_request.json() == {}

        # dados=None
        resposta = cliente_http.enviar("empty", dados=None)
        assert resposta == resposta_mock
        assert requests_mock.last_request.text in (None, "")

    def test_resposta_nao_json(self, cliente_http, requests_mock):
        """Testa resposta 200 com corpo não-JSON."""
        requests_mock.get(
            f"{cliente_http.url_base}/plain_text",
            text="OK - Texto simples.",
            status_code=200,
        )

        resposta = cliente_http.obter("plain_text")

        assert "Requisição bem-sucedida, mas resposta não é JSON" in resposta["mensagem"]
        assert resposta["resposta_bruta"].startswith("OK - Texto simples.")


# =============================================================================
# ERROS HTTP
# =============================================================================

class TestErrosHttp:

    def test_erro_400(self, cliente_http, requests_mock):
        """Deve levantar OpenAIBadRequestError para status 400."""
        requests_mock.post(
            f"{cliente_http.url_base}/bad_request",
            json={"error": {"message": "Parâmetro inválido", "type": "invalid_request_error"}},
            status_code=400,
        )

        with pytest.raises(OpenAIBadRequestError) as exc:
            cliente_http.enviar("bad_request", dados={})

        assert "400 - Bad Request" in str(exc.value)
        assert "Parâmetro inválido" in str(exc.value)

    def test_erro_400_resposta_nao_json(self, cliente_http, requests_mock):
        """Deve levantar OpenAIBadRequestError mesmo com resposta não-JSON."""
        texto = "Bad Request: Invalid input from upstream"
        requests_mock.post(
            f"{cliente_http.url_base}/bad_request_nojson",
            text=texto,
            status_code=400,
        )

        with pytest.raises(OpenAIBadRequestError) as exc:
            cliente_http.enviar("bad_request_nojson", dados={})

        assert "400 - Bad Request" in str(exc.value)
        assert requests_mock.call_count >= 1

    def test_erro_401(self, cliente_http, requests_mock):
        """Deve levantar OpenAIAuthenticationError para status 401."""
        requests_mock.get(
            f"{cliente_http.url_base}/unauthorized",
            json={"error": {"message": "Chave API incorreta", "type": "authentication_error"}},
            status_code=401,
        )

        with pytest.raises(OpenAIAuthenticationError) as exc:
            cliente_http.obter("unauthorized")

        assert "401 - Unauthorized" in str(exc.value)
        assert "Chave API incorreta" in str(exc.value)

    def test_erro_403(self, cliente_http, requests_mock):
        """Deve levantar OpenAIAuthenticationError para status 403."""
        requests_mock.get(
            f"{cliente_http.url_base}/forbidden",
            json={"error": {"message": "Acesso negado", "type": "permission_error"}},
            status_code=403,
        )

        with pytest.raises(OpenAIAuthenticationError) as exc:
            cliente_http.obter("forbidden")

        assert "403 - Forbidden" in str(exc.value)
        assert "Acesso negado" in str(exc.value)

    def test_erro_404(self, cliente_http, requests_mock):
        """Deve levantar OpenAINotFoundError para status 404."""
        requests_mock.get(
            f"{cliente_http.url_base}/not_found",
            json={"error": {"message": "Recurso não encontrado", "type": "invalid_request_error"}},
            status_code=404,
        )

        with pytest.raises(OpenAINotFoundError) as exc:
            cliente_http.obter("not_found")

        assert "404 - Not Found" in str(exc.value)
        assert "Recurso não encontrado" in str(exc.value)

    def test_erro_429_sem_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIRateLimitError para status 429 sem retries."""
        cliente_http.max_tentativas = 0
        requests_mock.get(
            f"{cliente_http.url_base}/rate_limit",
            json={"error": {"message": "Limite de taxa excedido", "type": "rate_limit_error"}},
            status_code=429,
        )

        with pytest.raises(OpenAIRateLimitError) as exc:
            cliente_http.obter("rate_limit")

        assert "429 - Too Many Requests" in str(exc.value)
        assert "Limite de taxa excedido" in str(exc.value)
        assert requests_mock.call_count == 1

    def test_erro_429_com_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIRateLimitError após retries para status 429."""
        cliente_http.max_tentativas = 1
        cliente_http.fator_backoff = 0.001

        response_429 = requests.Response()
        response_429.status_code = 429
        response_429._content = b'{"error": {"message": "Limite de taxa excedido", "type": "rate_limit_error"}}'
        response_429.reason = "Too Many Requests"

        requests_mock.get(f"{cliente_http.url_base}/rate_limit_retry", exc=HTTPError(response=response_429))

        with pytest.raises(OpenAIRateLimitError) as exc:
            cliente_http.obter("rate_limit_retry")

        assert "429 - Too Many Requests" in str(exc.value)
        assert requests_mock.call_count == 2

    def test_erro_500_sem_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIServerError para status 500 sem retries."""
        cliente_http.max_tentativas = 0
        requests_mock.post(
            f"{cliente_http.url_base}/server_error",
            json={"error": {"message": "Erro interno do servidor", "type": "server_error"}},
            status_code=500,
        )

        with pytest.raises(OpenAIServerError) as exc:
            cliente_http.enviar("server_error", dados={})

        assert "500 - Internal Server Error" in str(exc.value)
        assert "Erro interno do servidor" in str(exc.value)
        assert requests_mock.call_count == 1

    def test_erro_500_com_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIServerError após retries para status 500."""
        cliente_http.max_tentativas = 1
        cliente_http.fator_backoff = 0.001

        response_500 = requests.Response()
        response_500.status_code = 500
        response_500._content = b'{"error": {"message": "Erro interno do servidor", "type": "server_error"}}'
        response_500.reason = "Internal Server Error"

        requests_mock.post(f"{cliente_http.url_base}/server_error_retry", exc=HTTPError(response=response_500))

        with pytest.raises(OpenAIServerError) as exc:
            cliente_http.enviar("server_error_retry", dados={})

        assert "500 - Internal Server Error" in str(exc.value)
        assert requests_mock.call_count == 2


# =============================================================================
# ERROS DE CONEXÃO E TIMEOUT
# =============================================================================

class TestErrosConexao:

    def test_timeout_sem_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAITimeoutError para Timeout sem retries."""
        cliente_http.max_tentativas = 0
        requests_mock.get(f"{cliente_http.url_base}/timeout", exc=Timeout)

        with pytest.raises(OpenAITimeoutError) as exc:
            cliente_http.obter("timeout")

        assert "Tempo limite excedido" in str(exc.value)
        assert isinstance(exc.value.original_exception, Timeout)
        assert requests_mock.call_count == 1

    def test_timeout_com_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIRetryError após retries por Timeout."""
        cliente_http.max_tentativas = 1
        cliente_http.fator_backoff = 0.001
        requests_mock.get(f"{cliente_http.url_base}/timeout_retry", exc=req_exc.Timeout)

        with pytest.raises(OpenAIRetryError) as exc:
            cliente_http.obter("timeout_retry")

        assert "Máximo de retries (1) excedido" in str(exc.value)
        assert isinstance(exc.value.original_exception, OpenAITimeoutError)
        assert isinstance(exc.value.original_exception.original_exception, req_exc.Timeout)

    def test_connection_error_sem_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIConnectionError sem retries."""
        cliente_http.max_tentativas = 0
        requests_mock.get(
            f"{cliente_http.url_base}/connection_error",
            exc=requests.exceptions.ConnectionError("Problema de rede"),
        )

        with pytest.raises(OpenAIConnectionError) as exc:
            cliente_http.obter("connection_error")

        assert "Erro de conexão para" in str(exc.value)
        assert isinstance(exc.value.original_exception, requests.exceptions.ConnectionError)
        assert requests_mock.call_count == 1

    def test_connection_error_com_retry(self, cliente_http, requests_mock):
        """Deve levantar OpenAIRetryError após retries por ConnectionError."""
        cliente_http.max_tentativas = 1
        cliente_http.fator_backoff = 0.001
        requests_mock.get(
            f"{cliente_http.url_base}/connection_retry",
            exc=req_exc.ConnectionError("Problema de rede"),
        )

        with pytest.raises(OpenAIRetryError) as exc:
            cliente_http.obter("connection_retry")

        assert "Máximo de retries (1) excedido" in str(exc.value)
        assert isinstance(exc.value.original_exception, OpenAIConnectionError)

    def test_request_exception_generica(self, cliente_http, requests_mock):
        """Deve levantar OpenAIClientError para RequestException genérica."""
        cliente_http.max_tentativas = 0
        requests_mock.get(
            f"{cliente_http.url_base}/generic_error",
            exc=RequestException("Erro desconhecido"),
        )

        with pytest.raises(OpenAIClientError) as exc:
            cliente_http.obter("generic_error")

        assert "Erro de requisição inesperado para" in str(exc.value)
        assert isinstance(exc.value.original_exception, RequestException)
        assert requests_mock.call_count == 1


# =============================================================================
# RETRY E BACKOFF
# =============================================================================

class TestRetryEBackoff:

    def test_retry_bem_sucedido(self, cliente_http, requests_mock):
        """Deve ter sucesso na segunda tentativa após falha 500 na primeira."""
        cliente_http.max_tentativas = 2
        cliente_http.fator_backoff = 0.001

        requests_mock.get(f"{cliente_http.url_base}/flaky", [
            {'json': {"error": {"message": "Erro temporário"}}, 'status_code': 500},
            {'json': {"status": "ok"}, 'status_code': 200},
        ])

        resposta = cliente_http.obter("flaky")

        assert resposta == {"status": "ok"}
        assert requests_mock.call_count == 2

    def test_backoff_exponencial(self, cliente_http, requests_mock):
        """Testa retry com backoff exponencial — sucesso na terceira tentativa."""
        chamadas = {'count': 0}
        respostas = [
            {'status_code': 500, 'json': {'error': {'message': 'Erro temporário'}}},
            {'status_code': 500, 'json': {'error': {'message': 'Erro temporário'}}},
            {'status_code': 200, 'json': {'result': 'ok'}},
        ]

        def responder(request, context):
            idx = chamadas['count']
            chamadas['count'] += 1
            context.status_code = respostas[idx]['status_code']
            return respostas[idx]['json']

        requests_mock.get(f"{cliente_http.url_base}/backoff", json=responder)

        sleep_original = time.sleep
        time.sleep = lambda x: None
        try:
            resposta = cliente_http.obter("backoff")
            assert resposta == {'result': 'ok'}
        finally:
            time.sleep = sleep_original


# =============================================================================
# RATE LIMITER
# =============================================================================

class TestRateLimiter:

    def test_rate_limiter_limita_requisicoes(self):
        """Rate limiter de 2 req/s deve atrasar 5 requisições em pelo menos 1.5s."""
        cliente = ClienteHttpOpenAI(max_requisicoes_por_segundo=2.0)

        class FakeResponse:
            def raise_for_status(self): pass
            def json(self): return {"ok": True}

        cliente.sessao.request = lambda *a, **k: FakeResponse()

        inicio = time.time()
        for _ in range(5):
            cliente._realizar_requisicao("GET", "models")
        fim = time.time()

        assert fim - inicio >= 1.5, f"Rate limiter insuficiente: {fim - inicio:.2f}s"


# =============================================================================
# MÉTRICAS DE USO
# =============================================================================

class TestMetricas:

    def test_metricas_sucesso_e_falha(self):
        """Deve registrar corretamente 1 sucesso e 1 falha nas métricas."""
        cliente = ClienteHttpOpenAI()

        class FakeResponse:
            def __init__(self, status_code=200):
                self.status_code = status_code
            def raise_for_status(self):
                if self.status_code != 200:
                    raise Exception("Erro", self)
            def json(self):
                return {"ok": True}

        cliente.sessao.request = lambda *a, **k: FakeResponse(200)
        cliente._realizar_requisicao("GET", "models")

        cliente.sessao.request = lambda *a, **k: FakeResponse(500)
        try:
            cliente._realizar_requisicao("GET", "models")
        except Exception:
            pass

        metricas = cliente.get_metricas()

        assert metricas['total_requisicoes'] == 2
        assert metricas['requisicoes_sucesso'] == 1
        assert metricas['requisicoes_falha'] == 1
        assert metricas['ultimos_status'][0] == 200
        assert metricas['ultimos_status'][1] in (500, 'erro')
