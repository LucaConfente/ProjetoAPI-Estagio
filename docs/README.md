# 📘 Guia do Projeto — OpenAI Integration Hub

> Integração completa com a API da OpenAI: backend FastAPI, frontend React, CLI e testes automatizados.

---

## 📁 Documentação

| Arquivo | Descrição |
|---|---|
| [`api_reference.md`](./api_reference.md) | Endpoints, métodos HTTP, exemplos de requisição e autenticação |
| [`architecture.md`](./architecture.md) | Estrutura de pastas, componentes principais e fluxo de requisição |
| [`commands.md`](./commands.md) | Comandos para rodar CLI, backend, frontend e testes |
| [`troubleshooting.md`](./troubleshooting.md) | Problemas comuns, dicas de debug e soluções |

---

## 🚀 Como Rodar

### Backend (FastAPI)
```bash
# Na raiz do projeto
$env:OPENAI_API_KEY="sua-chave-aqui"
$env:API_AUTH_TOKEN="API_LUCA"
python -m uvicorn uweb_interface.backend.app:app --reload
```
Acesse a documentação interativa em: `http://localhost:8000/docs`

### Frontend (React)
```bash
cd uweb_interface/frontend/react-app
npm install
npm start
```
Acesse em: `http://localhost:3000`

---

## 🏗️ Arquitetura

```
ProjetoAPI-Estagio/
├── src/                        # Módulos Python (lógica de negócio)
│   ├── chat.py                 # Módulo de chat com histórico
│   ├── completions.py          # Módulo de completions
│   ├── http_client.py          # Cliente HTTP para a OpenAI
│   ├── config.py               # Configurações do projeto
│   └── validators.py           # Validações de entrada
│
├── uweb_interface/
│   ├── backend/
│   │   ├── app.py              # Servidor FastAPI (rotas e middleware)
│   │   └── schemas.py          # Modelos Pydantic (request/response)
│   └── frontend/
│       └── react-app/src/
│           ├── pages/          # Chat, Completions, Home
│           ├── components/     # Layout, Navbar
│           └── assets/         # CSS global
│
└── testes/                     # Testes automatizados
    ├── test_chat_module.py
    ├── test_commands.py
    ├── test_http_client.py
    └── test_integracao.py
```

---

## 🔐 Autenticação

A API usa **Bearer Token**. Configure a variável de ambiente antes de rodar:

```bash
$env:API_AUTH_TOKEN="API_LUCA"
```

No frontend, crie o arquivo `.env` em `react-app/`:
```env
REACT_APP_API_TOKEN=API_LUCA
```

---

## 🤖 Modelos Utilizados

| Funcionalidade | Modelo | Observação |
|---|---|---|
| Chat | `gpt-4o` | Suporta texto e imagens |
| Completions | `gpt-3.5-turbo-instruct` | Temperatura recomendada: 0.1–0.9 |

---

## 🧪 Testes

```bash
# Na raiz do projeto
pytest testes/
```

---

## 📎 Formatos de Arquivo Suportados no Chat

| Tipo | Extensões |
|---|---|
| Imagens | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp` |
| Texto | `.txt`, `.csv` |

> ⚠️ PDF e PowerPoint não são suportados diretamente.

---

*Projeto de Estágio © 2026 — Desenvolvido por [LucaConfente](https://github.com/LucaConfente)*
