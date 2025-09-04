def validar_modelo(modelo: str):
    if not isinstance(modelo, str) or not modelo:
        raise ValueError("O parâmetro 'modelo' deve ser uma string não vazia.")

    return modelo

def validar_prompt(prompt: str):
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("O parâmetro 'prompt' deve ser uma string não vazia.")
    return prompt

def validar_mensagens(mensagens: list):
    if not isinstance(mensagens, list) or not mensagens:
        raise ValueError("O parâmetro 'mensagens' deve ser uma lista não vazia.")
    for m in mensagens:
        if not isinstance(m, dict) or "role" not in m or "content" not in m:
            raise ValueError("Cada mensagem deve ser um dicionário com 'role' e 'content'.")
    return mensagens

def validar_parametros_extras(params: dict, permitidos=None):
    if permitidos is None:
        permitidos = {"temperature", "max_tokens", "top_p", "n", "stream", "logprobs"}
    for k in params:
        if k not in permitidos:
            raise ValueError(f"Parâmetro extra não permitido: {k}")
    return params


if __name__ == "__main__":
    try:
        print(validar_modelo("gpt-3.5-turbo"))
        print(validar_prompt("Olá!"))
        print(validar_mensagens([{"role": "user", "content": "Oi"}]))
        print(validar_parametros_extras({"temperature": 0.7, "max_tokens": 10}))
    except Exception as e:
        print("Erro de validação:", e)
