import pytest
from src.context_manager import ContextManager
from src.completions import CompletionsModule
from src.validators import validar_modelo, validar_prompt
from src.formatters import formatar_resposta_completions, formatar_contexto

@pytest.mark.integration
def test_fluxo_completo_completions():
    ctx = ContextManager(max_length=5)
    ctx.adicionar_mensagem("user", "Diga um fato curioso sobre Python.")
    modelo = validar_modelo("gpt-3.5-turbo-instruct")
    prompt = validar_prompt("Diga um fato curioso sobre Python.")
    completions = CompletionsModule()
    resposta = completions.gerar_texto(prompt, modelo=modelo, max_tokens=30)
    texto = formatar_resposta_completions(resposta)
    contexto = formatar_contexto(ctx.get_contexto())
    assert isinstance(texto, str) and len(texto) > 0
    assert "Python" in prompt
    assert "user" in contexto

# Para rodar: pytest testes/test_integracao.py -m integration
