# 🔧 Troubleshooting

> Guia de solução para os problemas mais comuns do projeto.

---

## ❌ Erro 401 — Não Autorizado

### Causa 1: Chave OpenAI inválida
```
OpenAIAuthenticationError: 401 - Unauthorized
```
**Solução:**
```bash
# Verifica se a chave está setada
echo $env:OPENAI_API_KEY

# Seta novamente se estiver vazia
$env:OPENAI_API_KEY="sk-sua-chave-aqui"
```
- Acesse [platform.openai.com/api-keys](https://platform.openai.com/api-keys) e gere uma nova chave se necessário.

### Causa 2: Token da API interna inválido
O frontend não está enviando o Bearer Token correto.

**Solução:**
- Confirme que o `.env` do React tem: `REACT_APP_API_TOKEN=API_LUCA`
- Reinicie o React após alterar o `.env`: `Ctrl+C` → `npm start`
- Confirme que o backend tem: `$env:API_AUTH_TOKEN="API_LUCA"`

---

## ❌ Erro 404 — Modelo não encontrado

```
OpenAINotFoundError: 404 - The model `gpt-4-vision-preview` has been deprecated
```
**Solução:** Substitua modelos descontinuados pelos atuais:

| Modelo antigo | Substituto atual |
|---|---|
| `gpt-4-vision-preview` | `gpt-4o` |
| `text-davinci-003` | `gpt-3.5-turbo-instruct` |
| `gpt-4-0314` | `gpt-4o` |

---

## ❌ Erro 429 — Rate Limit

```
OpenAIRateLimitError: 429 - Too Many Requests
```
**Solução:**
- Aguarde alguns segundos e tente novamente
- O cliente já possui retry automático com backoff exponencial
- Verifique seus limites em [platform.openai.com/usage](https://platform.openai.com/usage)
- Considere adicionar um `time.sleep()` entre requisições em massa

---

## ❌ Erro 500 — Backend quebrado

**Diagnóstico:** Adicione traceback no `app.py` para ver o erro real:
```python
except Exception as e:
    import traceback
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))
```
Reinicie o backend e verifique o terminal.

**Causas comuns:**
- Modelo solicitado não existe na sua conta
- Parâmetros inválidos no body da requisição
- Arquivo enviado em formato não suportado (PDF, PowerPoint)
- Variável de ambiente `OPENAI_API_KEY` não carregada

---

## ❌ Timeout ou ConnectionError

```
OpenAITimeoutError / OpenAIConnectionError
```
**Solução:**
- Verifique sua conexão com a internet
- Aumente o timeout em `src/config.py`
- Aguarde alguns minutos — pode ser instabilidade na OpenAI
- Verifique o status em [status.openai.com](https://status.openai.com)

---

## ❌ Frontend não atualiza após mudança no código

**Solução:**
```bash
# Para o servidor
Ctrl+C

# Limpa cache e reinicia
npm start
```
Se ainda não atualizar, force o reload no navegador com `Ctrl+Shift+R`.

---

## ❌ `Module not found: uweb_interface`

```
ModuleNotFoundError: No module named 'uweb_interface'
```
**Causa:** O uvicorn está sendo rodado de dentro de uma subpasta.

**Solução:** Rode sempre da **raiz do projeto**:
```bash
cd C:\Luca\Projeto Estagio API\ProjetoAPI-Estagio
python -m uvicorn uweb_interface.backend.app:app --reload
```

---

## ❌ Variável de ambiente não carrega

**Sintoma:** `echo $env:OPENAI_API_KEY` retorna vazio mesmo após setar.

**Causa:** A variável foi setada em outro terminal ou sessão.

**Solução:** Sete e rode o backend **no mesmo terminal, na mesma sessão**:
```bash
$env:OPENAI_API_KEY="sk-sua-chave"
$env:API_AUTH_TOKEN="API_LUCA"
python -m uvicorn uweb_interface.backend.app:app --reload
```

> Para persistir entre sessões, adicione ao `.env` na raiz do projeto.

---

## ❌ Completions retornando texto aleatório/incoerente

**Causa:** Temperatura muito alta ou prompt muito curto/ambíguo.

**Solução:**
- Use temperatura entre **0.1 e 0.7**
- Escreva prompts mais específicos e completos
- Aumente o `max_tokens` para pelo menos **150**
- Exemplo de prompt bom: `"Explique em português o que é machine learning:"`

---

## ❌ Arquivo rejeitado no chat

**Causa:** Formato não suportado (PDF, PowerPoint, Excel, etc.)

**Formatos aceitos:**
- Imagens: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Texto: `.txt`, `.csv`

---

## 🔍 Ferramentas de Diagnóstico

### Logs detalhados
```bash
# No .env
LOG_LEVEL=DEBUG
```

### Testar endpoints manualmente
```bash
# Testar health
curl http://localhost:8000/health

# Testar chat com autenticação
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer API_LUCA" \
  -d '{"messages": [{"role": "user", "content": "olá"}], "model": "gpt-4o"}'
```

### Verificar se o backend está rodando
Acesse `http://localhost:8000/health` no navegador — deve retornar `{"status": "ok"}`.

### Verificar se o frontend está conectando
Abra o DevTools (`F12`) → aba **Network** → envie uma mensagem → veja a requisição `/chat` e o status retornado.

---

*Veja também: [`api_reference.md`](./api_reference.md) · [`architecture.md`](./architecture.md) · [`commands.md`](./commands.md)*
