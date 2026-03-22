# 🏗️ Arquitetura do Projeto

> Visão geral da estrutura, componentes e fluxo de dados do OpenAI Integration Hub.

---

## 📁 Estrutura de Pastas

```
ProjetoAPI-Estagio/
│
├── src/                          # Lógica de negócio (Python)
│   ├── chat.py                   # Módulo de chat com histórico de mensagens
│   ├── completions.py            # Módulo de text completions
│   ├── http_client.py            # Cliente HTTP para a OpenAI (retry, rate limit, métricas)
│   ├── config.py                 # Configuração global singleton
│   ├── validators.py             # Validações de entrada
│   ├── formatters.py             # Formatação de respostas
│   ├── context_manager.py        # Gerenciamento de contexto de conversa
│   └── exceptions.py             # Exceções customizadas
│
├── testes/                       # Testes automatizados (pytest)
│   ├── test_chat_module.py
│   ├── test_commands.py
│   ├── test_http_client.py
│   └── test_integracao.py
│
├── docs/                         # Documentação técnica
│   ├── api_reference.md
│   ├── architecture.md
│   ├── commands.md
│   └── troubleshooting.md
│
├── uweb_interface/               # Interface Web
│   ├── backend/
│   │   ├── app.py                # Servidor FastAPI (rotas, CORS, autenticação)
│   │   └── schemas.py            # Modelos Pydantic (request/response)
│   └── frontend/
│       └── react-app/
│           └── src/
│               ├── pages/        # Home.js, Chat.js, Completions.js
│               ├── components/   # Layout.js (navbar)
│               └── assets/       # global.css (design system)
│
├── .env                          # Variáveis de ambiente (não versionar)
├── requirements.txt              # Dependências Python
└── pytest.ini                    # Configuração dos testes
```

---

## 🧩 Componentes Principais

### `ClienteHttpOpenAI` — `src/http_client.py`
Classe central de comunicação com a API da OpenAI. Implementada **sem SDKs oficiais**.

Responsabilidades:
- Execução de requisições `GET` e `POST`
- Retry automático com **backoff exponencial**
- **Rate limiter** local para controle de requisições por segundo
- Conversão de erros HTTP em exceções customizadas
- Coleta de **métricas de uso** (total, sucesso, falha, tempo médio)

---

### `Config` — `src/config.py`
Singleton que centraliza todas as configurações do projeto.

Parâmetros gerenciados:
- Chave da API OpenAI (`OPENAI_API_KEY`)
- URL base da API
- Timeout de requisições
- Número máximo de retries
- Fator de backoff exponencial

---

### `ChatModule` — `src/chat.py`
Gerencia conversas com histórico de mensagens. Recebe uma lista de mensagens no formato OpenAI e retorna a resposta do modelo.

---

### `FastAPI App` — `uweb_interface/backend/app.py`
Servidor REST que expõe os módulos Python como endpoints HTTP. Responsável por:
- Autenticação via **Bearer Token**
- Configuração de **CORS**
- Validação de payloads via **Pydantic**
- Roteamento para `ChatModule` e `ClienteHttpOpenAI`

---

### `React Frontend` — `uweb_interface/frontend/`
Interface web com três páginas:

| Página | Rota | Função |
|---|---|---|
| Home | `/` | Apresentação e navegação |
| Chat | `/chat` | Conversa com GPT-4o, suporte a arquivos |
| Completions | `/completions` | Teste de prompts com controle de parâmetros |

---

## 🔄 Fluxo de Requisição

```
Usuário (Browser)
      │
      │  HTTP POST /chat
      ▼
┌─────────────────┐
│   FastAPI App   │  ← Valida token Bearer
│   (app.py)      │  ← Valida body via Pydantic
└────────┬────────┘
         │
         │  Chama ChatModule
         ▼
┌─────────────────┐
│   ChatModule    │  ← Monta mensagens com histórico
│   (chat.py)     │  ← Processa arquivos (imagem/texto)
└────────┬────────┘
         │
         │  Chama ClienteHttpOpenAI
         ▼
┌──────────────────────┐
│ ClienteHttpOpenAI    │  ← Aplica rate limit
│ (http_client.py)     │  ← Executa requisição HTTP
│                      │  ← Retry com backoff se falhar
│                      │  ← Registra métricas
└────────┬─────────────┘
         │
         │  HTTPS
         ▼
   API da OpenAI
         │
         │  Resposta JSON
         ▼
┌─────────────────┐
│   FastAPI App   │  ← Serializa resposta (Pydantic)
└────────┬────────┘
         │
         ▼
Usuário (Browser)  ← Exibe mensagem no chat
```

---

## 🧪 Testes e Qualidade

| Arquivo | O que testa |
|---|---|
| `test_http_client.py` | Retry, backoff, erros HTTP, métricas, rate limit |
| `test_chat_module.py` | Criação de conversas, histórico, modelos |
| `test_commands.py` | Comandos CLI |
| `test_integracao.py` | Fluxo completo de ponta a ponta |

### Rodar os testes
```bash
pytest testes/
pytest testes/ -v          # verbose
pytest testes/ --tb=short  # erros resumidos
```

---

## 🔒 Segurança

- **Autenticação**: Bearer Token em todos os endpoints sensíveis
- **CORS**: Configurado para aceitar requisições do frontend
- **Variáveis de ambiente**: Chaves e tokens nunca hardcoded no código
- **Validação**: Todos os inputs validados via Pydantic antes de processar

---

*Veja também: [`api_reference.md`](./api_reference.md) · [`commands.md`](./commands.md) · [`troubleshooting.md`](./troubleshooting.md)*
