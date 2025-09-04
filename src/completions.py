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
