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
```

# Endpoints REST da API (FastAPI)

## Autenticação
Todos os endpoints (exceto `/` e `/health`) exigem Bearer Token:

```
Authorization: Bearer <API_AUTH_TOKEN>
```

## Endpoints

### GET /
Mensagem de status da API (confirma que está rodando).

### GET /health
Verifica se a API está funcionando (retorna `{ "status": "ok" }`).

### GET /models
Lista os modelos disponíveis na sua conta OpenAI.
**Requer autenticação.**

### GET /config
Retorna a configuração atual da API (ex: variáveis de ambiente carregadas).
**Requer autenticação.**

### POST /completions
Gera texto a partir de um prompt usando modelos do tipo "completion" (se disponíveis).
**Requer autenticação.**

Exemplo de corpo:
```json
{
  "prompt": "Diga olá em inglês.",
  "model": "text-davinci-003",
  "max_tokens": 20,
  "temperature": 0.5
}
```

### POST /chat
Envia mensagens para o modelo de chat (ex: gpt-3.5-turbo, gpt-4) e recebe respostas reais.
**Requer autenticação.**

Exemplo de corpo:
```json
{
  "messages": [
    { "role": "user", "content": "Explique buracos negros." }
  ],
  "model": "gpt-3.5-turbo"
}
```

### GET /docs
Interface Swagger interativa para testar e visualizar todos os endpoints.

### GET /auth-check
Retorna `{ "detail": "Autorização concedida!" }` se o token estiver correto.
**Requer autenticação.**

## CORS
O backend está configurado para aceitar requisições de diferentes origens (CORS), permitindo integração com frontends web.

## Observações
- Todos os endpoints retornam erros claros em caso de autenticação inválida ou falta de parâmetros.
- Para produção, ajuste `allow_origins` no CORS para maior segurança.
