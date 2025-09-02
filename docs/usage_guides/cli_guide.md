# Guia de Uso: CLI

## Introdução
A interface de linha de comando (CLI) permite interagir com a API OpenAI de forma simples e automatizada.

## Comandos Disponíveis
- `obter <endpoint>`: Realiza requisição GET para o endpoint informado.
- `enviar <endpoint> <dados>`: Realiza requisição POST com dados JSON.

## Exemplos de Uso
```bash
# Consultar modelos disponíveis
python -m cli.main obter models

# Enviar mensagem para chat/completions
python -m cli.main enviar chat/completions '{"messages": [{"role": "user", "content": "Olá"}]}'
```

## Configuração
- Configure a chave da API e parâmetros em `src/config.py` ou via variáveis de ambiente.

## Tratamento de Erros
- Mensagens de erro detalhadas são exibidas para problemas de autenticação, limite de taxa, erros de requisição e falhas de conexão.

## Testes
- Todos os comandos são cobertos por testes automatizados em `testes/test_commands.py`.
