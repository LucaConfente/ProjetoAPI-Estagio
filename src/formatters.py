import json
from typing import Any, Dict, List

def formatar_resposta_chat(resposta: Dict[str, Any]) -> str:
    """Formata a resposta do endpoint chat/completions para exibição amigável."""
    try:
        conteudo = resposta["choices"][0]["message"]["content"]
        return conteudo.strip()
    except Exception:
        return json.dumps(resposta, indent=2, ensure_ascii=False)

def formatar_resposta_completions(resposta: Dict[str, Any]) -> str:
    """Formata a resposta do endpoint completions para exibição amigável."""
    try:
        texto = resposta["choices"][0]["text"]
        return texto.strip()
    except Exception:
        return json.dumps(resposta, indent=2, ensure_ascii=False)

def formatar_contexto(mensagens: List[Dict[str, str]]) -> str:
    """Formata o histórico de contexto para exibição."""
    return "\n".join(f"[{m['role']}] {m['content']}" for m in mensagens)


if __name__ == "__main__":
    resposta_chat = {"choices": [{"message": {"content": "Olá! Como posso ajudar?"}}]}
    resposta_compl = {"choices": [{"text": "\n\nHello, world!"}]}
    contexto = [
        {"role": "user", "content": "Oi"},
        {"role": "assistant", "content": "Olá!"}
    ]
    print("Chat:", formatar_resposta_chat(resposta_chat))
    print("Completions:", formatar_resposta_completions(resposta_compl))
    print("Contexto:\n", formatar_contexto(contexto))
