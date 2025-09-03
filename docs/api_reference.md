# Referência da API

## ClienteHttpOpenAI
Implementa um cliente HTTP para a API OpenAI, com suporte a:
- Requisições GET e POST
- Lógica de retry com backoff exponencial
- Tratamento de erros customizados (400, 401, 403, 404, 429, 500, timeout, conexão)
- Métricas de uso
- Rate limiter local

### Principais métodos
- `obter(ponto_final, params=None)`: Realiza requisição GET.
- `enviar(ponto_final, dados=None)`: Realiza requisição POST.
- `_realizar_requisicao(metodo, ponto_final, **kwargs)`: Lógica central de requisição, retry e tratamento de erros.
- `get_metricas()`: Retorna métricas de uso.

### Exceções customizadas
- `OpenAIAuthenticationError`, `OpenAIBadRequestError`, `OpenAINotFoundError`, `OpenAIRateLimitError`, `OpenAIServerError`, `OpenAIClientError`, `OpenAITimeoutError`, `OpenAIConnectionError`, `OpenAIRetryError`.

### Configuração
- Utiliza a classe singleton `Config` para parâmetros como chave API, URL base, timeout, retries e backoff.

### Testes
- Testes automatizados em `testes/test_http_client.py` cobrem todos os cenários de erro, sucesso, retry e métricas.

# Referência da API

## Visão Geral
A biblioteca fornece integração direta via HTTP com a API da OpenAI, sem dependências de SDKs oficiais. Inclui tratamento avançado de erros, lógica de retry, rate limiter e métricas de uso.

## Principais Classes
### ClienteHttpOpenAI
- Cliente central para requisições à OpenAI.
- Suporte a GET, POST, retries, backoff exponencial, rate limiting e métricas.

#### Métodos
- `obter(ponto_final, params=None)`: Requisição GET para o endpoint.
- `enviar(ponto_final, dados=None)`: Requisição POST para o endpoint.
- `_realizar_requisicao(metodo, ponto_final, **kwargs)`: Lógica central de requisição, retry e tratamento de erros.
- `get_metricas()`: Retorna métricas de uso (total, sucesso, falha, tempo, status).

#### Exemplo de Uso
```python
from src.http_client import ClienteHttpOpenAI
cliente = ClienteHttpOpenAI()
resposta = cliente.obter('models')
print(resposta)
