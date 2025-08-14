# Contém todas as classes de exceção customizadas

class OpenAIClientError(Exception):
    """Exceção base para todos os erros do cliente OpenAI."""
    pass

class OpenAIAuthenticationError(OpenAIClientError):
    """Exceção para falhas de autenticação (e.g., 401 Unauthorized, 403 Forbidden)."""
    pass

class OpenAIBadRequestError(OpenAIClientError):
    """Exceção para requisições malformadas ou inválidas (e.g., 400 Bad Request)."""
    pass

class OpenAINotFoundError(OpenAIClientError):
    """Exceção para recursos não encontrados (e.g., 404 Not Found)."""
    pass

class OpenAIRateLimitError(OpenAIClientError):
    """Exceção para quando os limites de taxa da API são atingidos (e.g., 429 Too Many Requests)."""
    pass

class OpenAIServerError(OpenAIClientError):
    """Exceção para erros internos do servidor da OpenAI (e.g., 5xx Server Errors)."""
    pass

class OpenAIClientTimeoutError(OpenAIClientError):
    """Exceção para timeouts de conexão ou leitura."""
    pass

class OpenAIConnectionError(OpenAIClientError):
    """Exceção para problemas de conexão de rede."""
    pass

class OpenAIRetryError(OpenAIClientError):
    """Exceção para quando o número máximo de retries é excedido após várias tentativas."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class OpenAIAPIError(OpenAIClientError):
    """Exceção genérica para erros retornados pela API da OpenAI não mapeados especificamente."""
    def __init__(self, message, status_code=None, error_details=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_details = error_details
