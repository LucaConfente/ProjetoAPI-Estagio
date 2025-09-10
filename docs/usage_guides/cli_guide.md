## COMANDO PARA INICIALIZAR (TESTE)
- python -m cli.main enviar chat/completions --dados "{\"model\": \"gpt-3.5-turbo\", \"messages\": [{\"role\": \"user\", \"content\": \"Olá\"}]}"

## ENDPOINTS

GET /
Mensagem de status da API (confirma que está rodando).

GET /health
Verifica se a API está funcionando (retorna {"status": "ok"}).

GET /models
Lista os modelos disponíveis na sua conta OpenAI.

GET /config
Retorna a configuração atual da API (ex: variáveis de ambiente carregadas).

POST /completions
Gera texto a partir de um prompt usando modelos do tipo "completion" (se disponíveis).

POST /chat
Envia mensagens para o modelo de chat (ex: gpt-3.5-turbo, gpt-4) e recebe respostas reais.

GET /docs
Interface Swagger interativa para testar e visualizar todos os endpoints.