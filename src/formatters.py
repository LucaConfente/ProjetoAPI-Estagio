import json
from typing import Any, Dict, List
from colorama import Fore, Style, init

# Inicializa colorama para Windows
init(autoreset=True)

def formatar_resposta_chat(resposta: Dict[str, Any]) -> str:
    """Formata a resposta do endpoint chat/completions para exibição amigável e colorida."""
    try:
        conteudo = resposta["choices"][0]["message"]["content"]
        return f"{Fore.GREEN}{conteudo.strip()}{Style.RESET_ALL}"
    except Exception:
        return f"{Fore.YELLOW}{json.dumps(resposta, indent=2, ensure_ascii=False)}{Style.RESET_ALL}"

def formatar_resposta_completions(resposta: Dict[str, Any]) -> str:
    """Formata a resposta do endpoint completions para exibição amigável e colorida."""
    try:
        texto = resposta["choices"][0]["text"]
        return f"{Fore.GREEN}{texto.strip()}{Style.RESET_ALL}"
    except Exception:
        return f"{Fore.YELLOW}{json.dumps(resposta, indent=2, ensure_ascii=False)}{Style.RESET_ALL}"

def formatar_contexto(mensagens: List[Dict[str, str]]) -> str:
    """Formata o histórico de contexto para exibição com cores."""
    linhas = []
    for m in mensagens:
        if m['role'] == 'user':
            linhas.append(f"{Fore.CYAN}[user]{Style.RESET_ALL} {m['content']}")
        elif m['role'] == 'assistant':
            linhas.append(f"{Fore.MAGENTA}[assistant]{Style.RESET_ALL} {m['content']}")
        else:
            linhas.append(f"[{m['role']}] {m['content']}")
    return "\n".join(linhas)

# Funções para destacar erros e avisos
def formatar_erro(mensagem: str) -> str:
    """Formata mensagens de erro em vermelho."""
    return f"{Fore.RED}Erro: {mensagem}{Style.RESET_ALL}"

def formatar_aviso(mensagem: str) -> str:
    """Formata avisos em amarelo."""
    return f"{Fore.YELLOW}Aviso: {mensagem}{Style.RESET_ALL}"


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
