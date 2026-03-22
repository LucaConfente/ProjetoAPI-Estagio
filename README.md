# 🚀 OpenAI Integration Hub

O OpenAI Integration Hub é um projeto que visa criar uma biblioteca modular e reutilizável para a integração com a API da OpenAI. Desenvolvido com uma abordagem from scratch (sem o uso da biblioteca oficial ou frameworks como LangChain), este hub centraliza todas as funcionalidades essenciais para interagir com modelos de IA.

Com interfaces CLI e Web, ele oferece flexibilidade para desenvolvedores e uma experiência amigável para usuários. Este projeto é um exemplo prático de como construir integrações robustas e manuteníveis, focando em princípios de clean code, tratamento de erros e otimização.

# Passo a Passo Completo

## 1. Instalação dos Requisitos

```bash
pip install -r requirements.txt
```

## 2. Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo (exemplo):

```
OPENAI_API_KEY=sua_chave_openai_aqui
API_AUTH_TOKEN=API_LUCA  # ou outro token seguro
LOG_LEVEL=INFO
```

> **Atenção:** Nunca compartilhe sua chave da OpenAI publicamente.

## 3. Rodando o Backend (FastAPI)

```bash
python run.py
```
Ou, se preferir, diretamente com Uvicorn:
```bash
python -m uvicorn uweb_interface.backend.app:app --reload
```

Acesse a documentação interativa em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 4. Rodando o Frontend (React)

```bash
cd uweb_interface/frontend/react-app
npm install
npm start
```

Acesse o frontend em: [http://localhost:3000](http://localhost:3000)

## 5. Autenticação

A maioria dos endpoints exige autenticação Bearer Token. Use o valor de `API_AUTH_TOKEN` do seu `.env`.

No Swagger UI, clique em "Authorize" e insira o token.
No Postman/curl, adicione o header:
```
Authorization: Bearer API_LUCA
```

## 6. Principais Endpoints

- `GET /` — Status da API
- `GET /health` — Health check
- `GET /models` — Lista de modelos (autenticado)
- `GET /config` — Configuração da API (autenticado)
- `POST /completions` — Geração de texto (autenticado)
- `POST /chat` — Chat com IA (autenticado)
- `GET /docs` — Swagger UI
- `GET /auth-check` — Testa se o token está correto

## 7. Exemplos de Uso

### Exemplo de requisição para `/chat` (curl):
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Authorization: Bearer API_LUCA" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Olá!"}],"model":"gpt-3.5-turbo"}'
```

### Exemplo de requisição para `/completions` (curl):
```bash
curl -X POST "http://127.0.0.1:8000/completions" \
  -H "Authorization: Bearer API_LUCA" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Diga olá em inglês.", "model": "text-davinci-003", "max_tokens": 20, "temperature": 0.5}'
```

## 8. Testes Automatizados

Para rodar todos os testes:
```bash
pytest testes/
```
Para rodar um teste específico:
```bash
pytest testes/test_chat_module.py
```

## 9. CORS

O backend já está configurado para aceitar requisições de diferentes origens (CORS), permitindo integração com frontends web.

## 10. Documentação Detalhada

- [Referência da API (endpoints, exemplos, autenticação)](docs/api_reference.md)
- [Guia de uso da CLI](docs/usage_guides/cli_guide.md)
- [Arquitetura do sistema](docs/architecture.md)
- [Comandos e execução](docs/commands.md)
- [Troubleshooting e FAQ](docs/troubleshooting.md)

---

Esses passos garantem que qualquer pessoa consiga rodar, autenticar, testar e contribuir com o projeto rapidamente.



