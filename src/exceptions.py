
class OpenAIClientError(Exception):
    """
    Exceção base para todos os erros do cliente OpenAI.
    Todas as exceções customizadas devem herdar desta classe.
    """
    def __init__(self, message="Ocorreu um erro no cliente OpenAI.", details=None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self):
        if self.details:
            return f"{self.message} Detalhes: {self.details}"
        return self.message

# --- Exceções de Erros da API e Rede (já existentes, com base na OpenAIClientError refinada) ---

class OpenAIAuthenticationError(OpenAIClientError):
    """Exception for authentication failures (e.g., 401 Unauthorized, 403 Forbidden)."""
    # Pode herdar diretamente de OpenAIClientError ou adicionar atributos específicos
    def __init__(self, message="Falha na autenticação com a API OpenAI.", status_code=None, error_details=None):
        super().__init__(message, details=error_details)
        self.status_code = status_code
        self.error_details = error_details

class OpenAIBadRequestError(OpenAIClientError):
    """Exception for malformed or invalid requests (e.g., 400 Bad Request)."""
    def __init__(self, message="Requisição inválida para a API OpenAI.", status_code=None, error_details=None):
        super().__init__(message, details=error_details)
        self.status_code = status_code
        self.error_details = error_details

class OpenAINotFoundError(OpenAIClientError):
    """Exception for resources not found (e.g., 404 Not Found)."""
    def __init__(self, message="Recurso não encontrado na API OpenAI.", status_code=None, error_details=None):
        super().__init__(message, details=error_details)
        self.status_code = status_code
        self.error_details = error_details

class OpenAIRateLimitError(OpenAIClientError):
    """Exception for when API rate limits are reached (e.g., 429 Too Many Requests)."""
    def __init__(self, message="Limite de requisições da API OpenAI excedido.", status_code=None, error_details=None):
        super().__init__(message, details=error_details)
        self.status_code = status_code
        self.error_details = error_details

class OpenAIServerError(OpenAIClientError):
    """Exception for OpenAI internal server errors (e.g., 5xx Server Errors)."""
    def __init__(self, message="Erro interno do servidor da API OpenAI.", status_code=None, error_details=None):
        super().__init__(message, details=error_details)
        self.status_code = status_code
        self.error_details = error_details

class OpenAITimeoutError(OpenAIClientError):
    """Exception for connection or read timeouts."""
    def __init__(self, message="Tempo limite excedido na conexão com a API OpenAI.", original_exception=None):
        super().__init__(message, details=str(original_exception) if original_exception else None)
        self.original_exception = original_exception

class OpenAIConnectionError(OpenAIClientError):
    """Exception for network connection problems."""
    def __init__(self, message="Problema de conexão de rede com a API OpenAI.", original_exception=None):
        super().__init__(message, details=str(original_exception) if original_exception else None)
        self.original_exception = original_exception

class OpenAIRetryError(OpenAIClientError):
    """Exception for when maximum number of retries is exceeded after multiple attempts."""
    def __init__(self, message, original_exception=None):
        super().__init__(message, details=str(original_exception) if original_exception else None)
        self.original_exception = original_exception

class OpenAIAPIError(OpenAIClientError):
    """Generic exception for errors returned by OpenAI API not specifically mapped."""
    def __init__(self, message, status_code=None, error_details=None):
        super().__init__(message, details=error_details)
        self.status_code = status_code
        self.error_details = error_details

# --- Novas Implementações Sugeridas ---

class OpenAIConfigurationError(Exception): # Ou a sua exceção base customizada
    """
    Exceção levantada para erros de configuração relacionados à API OpenAI.
    """
    def __init__(self, message: str, details: str = None):
        """
        Inicializa a exceção de configuração da OpenAI.

        Args:
            message (str): A mensagem de erro principal.
            details (str, optional): Detalhes adicionais sobre o erro. Defaults to None.
        """
        super().__init__(message)
        self.details = details # Armazena os detalhes para acesso posterior, se necessário



class OpenAIConfigurationError(OpenAIClientError):
    """
    Exceção para erros relacionados à configuração do cliente OpenAI (ex: API Key ausente/inválida).
    """
    def __init__(self, message="Erro de configuração do cliente OpenAI.", config_key=None, expected_value=None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        if expected_value:
            details["expected_value"] = expected_value
        super().__init__(message, details=details if details else None)
        self.config_key = config_key
        self.expected_value = expected_value

class OpenAIValidationError(OpenAIClientError):
    """
    Exceção para erros de validação de dados de entrada antes de enviar para a API OpenAI.
    """
    def __init__(self, message="Erro de validação de dados de entrada.", field=None, value=None, expected_format=None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if expected_format:
            details["expected_format"] = expected_format
        super().__init__(message, details=details if details else None)
        self.field = field
        self.value = value
        self.expected_format = expected_format
