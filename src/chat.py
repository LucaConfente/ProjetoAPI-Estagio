from src.exceptions import OpenAIValidationError  
from src.http_client import ClienteHttpOpenAI     
from src.config import Config

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

if __name__ == "__main__":
    print("Módulo Chat executado diretamente.")

    chat = ChatModule()
    try:
        resposta = chat.criar_conversa([
            {"role": "user", "content": "Olá, tudo bem?"}
        ])
        print("Resposta da API:", resposta)
    except Exception as e:
        print("Erro ao criar conversa:", e)

# -------------------------------------------------------------------------------------------------
#
# Este módulo define a classe ChatModule, responsável por intermediar a criação
# de conversas com a API de chat da OpenAI. Ele valida as mensagens e o modelo
# recebidos, monta o payload e utiliza o ClienteHttpOpenAI para enviar a
# requisição ao endpoint "chat/completions" da OpenAI.
#
# Principais pontos:
# - Validação rigorosa dos parâmetros de entrada (mensagens e modelo).
# - Utilização de uma classe cliente HTTP dedicada para abstrair a comunicação.
# - Lança exceções customizadas (OpenAIValidationError) em caso de erro de uso.
# - Pode ser executado diretamente para testes rápidos, exibindo a resposta da API.
#
# Uso típico:
#   chat = ChatModule()
#   resposta = chat.criar_conversa([
#       {"role": "user", "content": "Olá!"}
#   ])
#
# Este arquivo faz parte da camada de backend do projeto, servindo como ponte
# entre a lógica de negócio e a API da OpenAI para funcionalidades de chat.
