from src.context_manager import ContextManager
from src.completions import CompletionsModule
from src.validators import validar_modelo, validar_prompt
from src.formatters import formatar_resposta_completions, formatar_contexto

# 1. Gerenciar contexto
ctx = ContextManager(max_length=5)
ctx.adicionar_mensagem("user", "Olá, IA!")
ctx.adicionar_mensagem("assistant", "Olá! Como posso ajudar?")
ctx.adicionar_mensagem("user", "Me dê uma dica de Python.")

# 2. Validar entrada
modelo = validar_modelo("gpt-3.5-turbo-instruct")
prompt = validar_prompt("Me dê uma dica de Python.")

# 3. Gerar texto com completions
completions = CompletionsModule()
resposta = completions.gerar_texto(prompt, modelo=modelo, max_tokens=30)

# 4. Formatar e exibir resultados
print("Contexto da conversa:")
print(formatar_contexto(ctx.get_contexto()))
print("\nResposta da IA:")
print(formatar_resposta_completions(resposta))