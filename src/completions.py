from src.exceptions import OpenAIValidationError
from src.http_client import ClienteHttpOpenAI
from src.config import Config

class CompletionsModule:
    def __init__(self):
        self.cliente_http = ClienteHttpOpenAI()

    def gerar_texto(self, prompt: str, modelo: str = "text-davinci-003", **kwargs):
        if not isinstance(prompt, str) or not prompt:
            raise OpenAIValidationError("O parâmetro 'prompt' deve ser uma string não vazia.", field="prompt")
        if not isinstance(modelo, str) or not modelo:
            raise OpenAIValidationError("O parâmetro 'modelo' deve ser uma string não vazia.", field="modelo")
        payload = {"model": modelo, "prompt": prompt}
        payload.update(kwargs)  # Permite parâmetros extras como temperature, max_tokens, etc.
        return self.cliente_http.enviar("completions", dados=payload)

if __name__ == "__main__":
    print("Módulo Completions executado diretamente.")
    completions = CompletionsModule()
    try:
        resposta = completions.gerar_texto("Olá, mundo!", modelo="gpt-3.5-turbo-instruct", max_tokens=20)
        print("Resposta da API:", resposta)
    except Exception as e:
        print("Erro ao gerar texto:", e)

# ---------------------------------------------------------------------------------------------
#
# Este módulo define a classe CompletionsModule, responsável por intermediar
# a geração de textos usando a API de completions da OpenAI. Ele valida o prompt
# e o modelo recebidos, monta o payload e utiliza o ClienteHttpOpenAI para enviar
# a requisição ao endpoint "completions" da OpenAI.
#
# Principais pontos:
# - Validação dos parâmetros de entrada (prompt e modelo).
# - Permite parâmetros extras (como temperature, max_tokens, etc) via **kwargs.
# - Utilização de uma classe cliente HTTP dedicada para abstrair a comunicação.
# - Lança exceções customizadas (OpenAIValidationError) em caso de erro de uso.
# - Pode ser executado diretamente para testes rápidos, exibindo a resposta da API.
#
# Uso típico:
#   completions = CompletionsModule()
#   resposta = completions.gerar_texto(
#       "Texto de entrada",
#       modelo="text-davinci-003", ( modelo descontinuado, usar "gpt-3.5-turbo-instruct" )
#       max_tokens=50,
#       temperature=0.7
#   )
#
# Este arquivo faz parte da camada de backend do projeto, servindo como ponte
# entre a lógica de negócio e a API da OpenAI para funcionalidades de geração de texto.
