# ⚡ Comandos do Projeto

> Referência completa de comandos para rodar, testar e interagir com o OpenAI Integration Hub.

---

## 🚀 Backend (FastAPI)

```bash
# Na raiz do projeto — configura as variáveis e sobe o servidor
$env:OPENAI_API_KEY="sk-sua-chave-aqui"
$env:API_AUTH_TOKEN="API_LUCA"
python -m uvicorn uweb_interface.backend.app:app --reload
```

> O servidor sobe em `http://localhost:8000`

### Endpoints disponíveis

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da API |
| `GET` | `/health` | Verifica se está rodando |
| `GET` | `/models` 🔒 | Lista modelos disponíveis |
| `GET` | `/config` 🔒 | Configuração atual |
| `GET` | `/auth-check` 🔒 | Valida o token |
| `POST` | `/chat` | Envia mensagem ao modelo |
| `POST` | `/completions` 🔒 | Gera texto via prompt |
| `GET` | `/docs` | Swagger UI interativo |
| `GET` | `/redoc` | Documentação ReDoc |

> 🔒 Requer header `Authorization: Bearer API_LUCA`

---

## 🌐 Frontend (React)

```bash
# Entra na pasta e instala dependências (só na primeira vez)
cd uweb_interface/frontend/react-app
npm install

# Roda o servidor de desenvolvimento
npm start
```

> O frontend sobe em `http://localhost:3000`

```bash
# Gerar build de produção
npm run build
```

---

## 🖥️ CLI

```bash
# Modo interativo (menu guiado)
python -m cli.main interativo

# Comandos diretos
python -m cli.main chat               # Inicia uma conversa
python -m cli.main completions        # Gera texto via prompt
python -m cli.main listar_modelos     # Lista modelos disponíveis
python -m cli.main config             # Exibe configuração atual
python -m cli.main test_connection    # Testa conexão com a OpenAI
python -m cli.main obter              # Requisição GET manual
python -m cli.main enviar             # Requisição POST manual
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest testes/

# Com output detalhado
pytest testes/ -v

# Com erros resumidos
pytest testes/ --tb=short

# Rodar um arquivo específico
pytest testes/test_chat_module.py
pytest testes/test_http_client.py
pytest testes/test_commands.py
pytest testes/test_integracao.py

# Rodar um teste específico pelo nome
pytest testes/ -k "test_retry"
pytest testes/ -k "test_autenticacao"

# Ver cobertura de código (requer pytest-cov)
pytest testes/ --cov=src
```

---

## 🐛 Debug — Módulos Isolados

> Útil para testar módulos individualmente durante o desenvolvimento.

```bash
python -m src.chat
python -m src.http_client
python -m src.config
python -m src.exceptions
```

> ⚠️ Para rodar isoladamente, o módulo precisa ter:
> ```python
> if __name__ == "__main__":
>     # código de teste
> ```

---

## 🔧 Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Desativar
deactivate
```

---

## 🔑 Variáveis de Ambiente

```bash
# PowerShell (temporário — só para a sessão atual)
$env:OPENAI_API_KEY="sk-sua-chave-aqui"
$env:API_AUTH_TOKEN="API_LUCA"

# Verificar se foi setado
echo $env:OPENAI_API_KEY
echo $env:API_AUTH_TOKEN
```

> Para persistir, adicione ao arquivo `.env` na raiz do projeto:
> ```env
> OPENAI_API_KEY=sk-sua-chave-aqui
> API_AUTH_TOKEN=API_LUCA
> ```

---

*Veja também: [`api_reference.md`](./api_reference.md) · [`architecture.md`](./architecture.md) · [`troubleshooting.md`](./troubleshooting.md)*
