class OpenAIClientError(Exception):  # Must inherit from 'Exception'
    """Base exception for all OpenAI client errors."""
    pass

class OpenAIAuthenticationError(OpenAIClientError):
    """Exception for authentication failures (e.g., 401 Unauthorized, 403 Forbidden)."""
    pass

class OpenAIBadRequestError(OpenAIClientError):
    """Exception for malformed or invalid requests (e.g., 400 Bad Request)."""
    pass

class OpenAINotFoundError(OpenAIClientError):
    """Exception for resources not found (e.g., 404 Not Found)."""
    pass

class OpenAIRateLimitError(OpenAIClientError):
    """Exception for when API rate limits are reached (e.g., 429 Too Many Requests)."""
    pass

class OpenAIServerError(OpenAIClientError):
    """Exception for OpenAI internal server errors (e.g., 5xx Server Errors)."""
    pass

class OpenAITimeoutError(OpenAIClientError):
    """Exception for connection or read timeouts."""
    pass

class OpenAIConnectionError(OpenAIClientError):
    """Exception for network connection problems."""
    pass

class OpenAIRetryError(OpenAIClientError):
    """Exception for when maximum number of retries is exceeded after multiple attempts."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class OpenAIAPIError(OpenAIClientError):
    """Generic exception for errors returned by OpenAI API not specifically mapped."""
    def __init__(self, message, status_code=None, error_details=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_details = error_details