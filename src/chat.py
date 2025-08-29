from .exceptions import OpenAIValidationError  
from .http_client import ClienteHttpOpenAI     
from .config import Config

class ChatModule:   
    def __init__(self):
        self.cliente_http = ClienteHttpOpenAI()

    def criar_conversa(self, mensagens: list, modelo: str = "gpt-3.5-turbo"):
        if not isinstance(mensagens, list) or not mensagens:
            raise OpenAIValidationError("O parâmetro 'mensagens' deve ser uma lista não vazia de objetos de mensagem.", field="mensagens")
        if not all(isinstance(m, dict) and "role" in m and "content" in m for m in mensagens):
            raise OpenAIValidationError("Cada mensagem deve ser um dicionário com 'role' e 'content'.", field="mensagens")
        if not isinstance(modelo, str) or not modelo:
            raise OpenAIValidationError("O parâmetro 'modelo' deve ser uma string não vazia.", field="modelo")

        payload = {"model": modelo, "messages": mensagens}
        return self.cliente_http.enviar("chat/completions", dados=payload)