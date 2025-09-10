# Comandos para Executar Arquivos do Projeto

## CLI (com Click)
```
python -m cli.main interativo
python -m cli.main chat
python -m cli.main obter
python -m cli.main enviar
python -m cli.main config
python -m cli.main test_connection
python -m cli.main listar_modelos
```

---

## Módulos principais (`src/`)
> Para rodar módulos diretamente (útil para debug ou testes manuais):
```
python -m src.chat
python -m src.config
python -m src.exceptions
python -m src.http_client
python -m src.http_status_reasons
python -m src.logconfig
```
> (Se algum módulo não tiver bloco `if __name__ == "__main__":`, pode ser necessário adicionar para rodar isoladamente.)

---

## Testes unitários e de integração (`testes/`)
> Para rodar todos os testes:
```
pytest testes/
```
> Para rodar um teste específico:
```
pytest testes/test_chat_module.py
pytest testes/test_commands.py
pytest testes/test_http_client.py
```
> Para rodar um teste diretamente (não recomendado, mas possível):
```
python -m testes.test_chat_module
python -m testes.test_commands
python -m testes.test_http_client
```

---

## CLI - Submódulos (`cli/commands/`)
> Para rodar diretamente (se tiver bloco main):
```
python -m cli.commands.chat
python -m cli.commands.completions
```

---

## Web Interface (se aplicável)
> Backend:
```
python -m uweb_interface.backend.app
python -m uweb_interface.backend.controllers
python -m uweb_interface.backend.routes
python -m uweb_interface.backend.schemas
```
> Frontend (Node.js/React):  
Entre na pasta e use:
```
cd uweb_interface/frontend
npm start
```
ou
```
npm run dev
```

---

Se algum arquivo não rodar diretamente, adicione um bloco:
```python
if __name__ == "__main__":
    # código de teste ou execução
```

Se precisar de comandos para arquivos específicos ou exemplos de uso, só pedir!


## FASTAPI COMANDOS 

/ — Mensagem de status da API (GET)
/health — Verifica se a API está rodando (GET)
/models — Lista os modelos disponíveis (GET)
/config — Mostra a configuração atual da API (GET)
/completions — Gera texto a partir de um prompt (POST)
/chat — Envia mensagens para o modelo de chat (POST)
docs — Documentação interativa Swagger (GET)
/redoc — Outra visualização de documentação (GET)