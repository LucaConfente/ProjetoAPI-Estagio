# Troubleshooting (Resolução de Problemas)

## Erros Comuns
- **401 Unauthorized**: Verifique se a chave da API está correta.
- **429 Too Many Requests**: Aguarde e tente novamente; o cliente implementa retry automático.
- **500 Internal Server Error**: Pode ser problema temporário; o cliente tenta novamente com backoff exponencial.
- **Timeout/ConnectionError**: Verifique sua conexão de rede e o tempo limite configurado.

## Debug de Testes
- Use `pytest -v` para ver detalhes dos testes.
- Se um teste falhar, verifique se o método está levantando a exceção correta (ex: `OpenAIRetryError` para retries).
- Confira se o backoff está sendo registrado em `self._backoff_calls`.

## Dicas Gerais
- Sempre revise a configuração em `src/config.py`.
- Consulte os logs em `logs/app.log` para detalhes de execução.
- Para dúvidas sobre erros, consulte a documentação das exceções customizadas em `src/exceptions.py`.
