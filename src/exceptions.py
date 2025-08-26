class ErroClienteOpenAI(Exception): # Deve herdar de 'Exception'
    """Exceção base para todos os erros do cliente OpenAI."""
    pass

class ErroAutenticacaoOpenAI(ErroClienteOpenAI):
    """Exceção para falhas de autenticação (e.g., 401 Unauthorized, 403 Forbidden)."""
    pass

class ErroRequisicaoInvalidaOpenAI(ErroClienteOpenAI):
    """Exceção para requisições malformadas ou inválidas (e.g., 400 Bad Request)."""
    pass

class ErroNaoEncontradoOpenAI(ErroClienteOpenAI):
    """Exceção para recursos não encontrados (e.g., 404 Not Found)."""
    pass

class ErroLimiteTaxaOpenAI(ErroClienteOpenAI):
    """Exceção para quando os limites de taxa da API são atingidos (e.g., 429 Too Many Requests)."""
    pass

class ErroServidorOpenAI(ErroClienteOpenAI):
    """Exceção para erros internos do servidor da OpenAI (e.g., 5xx Server Errors)."""
    pass

class ErroTempoLimiteClienteOpenAI(ErroClienteOpenAI):
    """Exceção para timeouts de conexão ou leitura."""
    pass

class ErroConexaoOpenAI(ErroClienteOpenAI):
    """Exceção para problemas de conexão de rede."""
    pass

class ErroTentativaNovamenteOpenAI(ErroClienteOpenAI):
    """Exceção para quando o número máximo de retries é excedido após várias tentativas."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class ErroAPIOpenAI(ErroClienteOpenAI):
    """Exceção genérica para erros retornados pela API da OpenAI não mapeados especificamente."""
    def __init__(self, message, status_code=None, error_details=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_details = error_details