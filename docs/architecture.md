# Arquitetura do Projeto

## Estrutura de Pastas
- `src/`: Código principal do cliente HTTP, configuração, exceções e utilitários.
- `cli/`: Interface de linha de comando para interação com a API.
- `testes/`: Testes automatizados (pytest) para todos os módulos.
- `docs/`: Documentação técnica e de uso.
- `uweb_interface/`: Interface web (frontend e backend).

## Componentes Principais
- **ClienteHttpOpenAI**: Classe central para comunicação com a API OpenAI, implementando lógica de retry, tratamento de erros e métricas.
- **Config**: Singleton para configuração global (chave API, URL, timeout, retries, backoff).
- **Exceções Customizadas**: Classes para tratamento granular de erros da API.
- **Rate Limiter**: Controle local de requisições por segundo.
- **Testes Automatizados**: Cobrem todos os fluxos críticos, incluindo erros, retries, backoff e métricas.

## Fluxo de Requisição
1. Usuário faz requisição via CLI, web ou diretamente pelo cliente.
2. ClienteHttpOpenAI executa a requisição, aplicando rate limit, timeout e lógica de retry.
3. Erros são tratados e convertidos em exceções customizadas.
4. Métricas são registradas para monitoramento.
5. Resposta é retornada ao usuário ou interface.

## Testes e Garantia de Qualidade
- Testes unitários e de integração garantem robustez do tratamento de erros, lógica de retry e métricas.
- Testes simulam cenários de sucesso, falha, timeout, conexão e backoff exponencial.
