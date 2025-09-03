# Troubleshooting

## Problemas Comuns

### 1. Erros de API Key
- Verifique se a variável `OPENAI_API_KEY` está definida corretamente no arquivo `.env`.
- Certifique-se de que não há espaços extras ou aspas na chave.
- Gere uma nova chave na plataforma OpenAI se necessário.

### 2. Falha de Autenticação (401/403)
- Confirme se a chave está ativa e válida.
- Verifique se o endpoint está correto.
- Cheque se o ambiente está carregando as variáveis corretamente.

### 3. Rate Limiting (429)
- Reduza o número de requisições por segundo.
- Utilize o rate limiter local do cliente.
- Aguarde alguns segundos antes de tentar novamente.

### 4. Timeout ou ConnectionError
- Verifique sua conexão com a internet.
- Aumente o valor de timeout na configuração.
- Tente novamente em alguns minutos.

### 5. Erros de Requisição (400/404/500)
- Confira se os parâmetros enviados estão corretos.
- Consulte a documentação dos endpoints.
- Para erros 500, tente novamente após alguns instantes.

## Ferramentas de Diagnóstico
- Use logs detalhados (`LOG_LEVEL=DEBUG` no `.env`) para identificar o ponto de falha.
- Utilize ferramentas como Postman ou httpie para testar endpoints manualmente.

## Recomendações Gerais
- Sempre mantenha a documentação e exemplos atualizados.
- Consulte os arquivos `docs/api_reference.md` e `docs/architecture.md` para detalhes técnicos.
- Em caso de dúvidas, revise os testes automatizados em `testes/` para exemplos de uso e tratamento de erros.
