# 📡 Referência da API

> Documentação completa dos endpoints REST e do cliente HTTP interno para integração com a OpenAI.

---

## 🔐 Autenticação

Todos os endpoints (exceto `/` e `/health`) exigem **Bearer Token** no header:

```http
Authorization: Bearer <API_AUTH_TOKEN>
```

Configure o token via variável de ambiente:
```bash
$env:API_AUTH_TOKEN="API_LUCA"   # PowerShell
export API_AUTH_TOKEN="API_LUCA"  # Linux/Mac
```

---

## 🌐 Endpoints REST (FastAPI)

### `GET /`
Confirma que a API está no ar.
```json
{ "message": "API rodando! Veja /docs para documentação." }
```

---

### `GET /health`
Verifica o status da API.
```json
{ "status": "ok" }
```

---

### `GET /auth-check` 🔒
Valida se o token de autenticação está correto.
```json
{ "detail": "Autorização concedida!" }
```

---

### `GET /models` 🔒
Lista todos os modelos disponíveis na conta OpenAI.

**Resposta:**
```json
{
  "models": ["gpt-4o", "gpt-3.5-turbo", "gpt-3.5-turbo-instruct", "..."]
}
```

---

### `GET /config` 🔒
Retorna a configuração atual carregada pelo sistema.

**Resposta:**
```json
{
  "config": {
    "api_url": "https://api.openai.com/v1",
    "timeout": 30,
    "max_retries": 3
  }
}
```

---

### `POST /chat` 🔒
Envia mensagens para o modelo de chat e recebe respostas. Suporta envio de imagens e arquivos de texto.

**Body:**
```json
{
  "messages": [
    { "role": "user", "content": "Explique buracos negros." }
  ],
  "model": "gpt-4o",
  "files": []
}
```

**Body com imagem:**
```json
{
  "messages": [
    { "role": "user", "content": "O que tem nessa imagem?" }
  ],
  "model": "gpt-4o",
  "files": [
    {
      "type": "image",
      "name": "foto.jpg",
      "mime": "image/jpeg",
      "data": "<base64>"
    }
  ]
}
```

**Body com arquivo de texto:**
```json
{
  "messages": [
    { "role": "user", "content": "Analise esse arquivo." }
  ],
  "model": "gpt-4o",
  "files": [
    {
      "type": "text",
      "name": "dados.csv",
      "mime": "text/csv",
      "data": "coluna1,coluna2\nvalor1,valor2"
    }
  ]
}
```

**Resposta:**
```json
{ "response": "Buracos negros são regiões do espaço-tempo onde..." }
```

---

### `POST /completions` 🔒
Gera texto a partir de um prompt usando modelos do tipo instruct.

**Body:**
```json
{
  "prompt": "Escreva uma introdução sobre inteligência artificial:",
  "model": "gpt-3.5-turbo-instruct",
  "max_tokens": 200,
  "temperature": 0.5
}
```

**Resposta:**
```json
{ "response": "A inteligência artificial é uma área da ciência da computação que..." }
```

> ⚠️ Temperatura recomendada: entre **0.1 e 0.9**. Valores acima de 1.0 podem gerar respostas incoerentes.

---

### `GET /docs`
Interface **Swagger UI** para testar e visualizar todos os endpoints interativamente.
Acesse em: `http://localhost:8000/docs`

---

## 🔧 Cliente HTTP Interno — `ClienteHttpOpenAI`

Implementação própria de cliente HTTP para a API da OpenAI, **sem dependência de SDKs oficiais**.

### Funcionalidades
- Requisições `GET` e `POST`
- Retry automático com **backoff exponencial**
- Rate limiter local
- Tratamento de erros customizados por código HTTP
- Métricas de uso

### Métodos Principais

| Método | Descrição |
|---|---|
| `obter(ponto_final, params=None)` | Requisição GET para o endpoint |
| `enviar(ponto_final, dados=None)` | Requisição POST para o endpoint |
| `get_metricas()` | Retorna métricas de uso acumuladas |
| `_realizar_requisicao(...)` | Lógica central de retry e tratamento de erros |

### Exemplo de Uso

```python
from src.http_client import ClienteHttpOpenAI

cliente = ClienteHttpOpenAI()

# Listar modelos
modelos = cliente.obter('models')
print(modelos)

# Enviar chat
resposta = cliente.enviar('chat/completions', dados={
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Olá!"}]
})
print(resposta)
```

### Métricas

```python
metricas = cliente.get_metricas()
# {
#   "total_requisicoes": 10,
#   "sucesso": 9,
#   "falha": 1,
#   "tempo_medio_ms": 430,
#   "status_codes": { "200": 9, "429": 1 }
# }
```

---

## ⚠️ Exceções Customizadas

| Exceção | Código HTTP | Causa |
|---|---|---|
| `OpenAIAuthenticationError` | 401 | Token da OpenAI inválido ou ausente |
| `OpenAIBadRequestError` | 400 | Parâmetros inválidos na requisição |
| `OpenAINotFoundError` | 404 | Modelo ou endpoint não encontrado |
| `OpenAIRateLimitError` | 429 | Limite de requisições atingido |
| `OpenAIServerError` | 500 | Erro interno na OpenAI |
| `OpenAITimeoutError` | — | Requisição excedeu o tempo limite |
| `OpenAIConnectionError` | — | Falha de conexão com a API |
| `OpenAIRetryError` | — | Todas as tentativas de retry falharam |

---

## 🔄 CORS

O backend aceita requisições de qualquer origem (`*`). Para produção, restrinja em `app.py`:

```python
allow_origins=["https://seu-dominio.com"]
```

---

## 📌 Observações

- O endpoint `/chat` não exige autenticação Bearer por padrão (configurável em `app.py`)
- Todos os outros endpoints retornam `401 Unauthorized` com token inválido
- A documentação Swagger em `/docs` permite testar endpoints com autenticação integrada

---

*Veja também: [`architecture.md`](./architecture.md) · [`commands.md`](./commands.md) · [`troubleshooting.md`](./troubleshooting.md)*
