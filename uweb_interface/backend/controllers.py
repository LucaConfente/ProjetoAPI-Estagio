from fastapi import HTTPException
from uweb_interface.backend.schemas import ChatRequest, ChatResponse, CompletionRequest, CompletionResponse, ModelListResponse, ConfigResponse
from src.chat import ChatModule
from src.http_client import ClienteHttpOpenAI
from src.config import Config


def handle_chat(payload: ChatRequest) -> ChatResponse:
    try:
        chat_module = ChatModule()
        mensagens = [m.dict() for m in payload.messages]

        # Processa arquivos se existirem
        if payload.files:
            content_parts = []

            last_msg = mensagens[-1] if mensagens else None
            if last_msg and last_msg.get('content'):
                content_parts.append({"type": "text", "text": last_msg['content']})

            for f in payload.files:
                if f.type == 'image':
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{f.mime};base64,{f.data}"
                        }
                    })
                elif f.type == 'text':
                    content_parts.append({
                        "type": "text",
                        "text": f"Conteúdo do arquivo '{f.name}':\n\n{f.data}"
                    })

            if mensagens:
                mensagens[-1] = {"role": "user", "content": content_parts}
            else:
                mensagens = [{"role": "user", "content": content_parts}]

        resposta = chat_module.criar_conversa(
            mensagens=mensagens,
            modelo=payload.model or "gpt-4o"
        )
        conteudo = resposta["choices"][0]["message"]["content"].strip()
        return ChatResponse(response=conteudo)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def handle_completions(payload: CompletionRequest) -> CompletionResponse:
    try:
        cliente = ClienteHttpOpenAI()
        dados = {
            "prompt": payload.prompt,
            "model": payload.model,
            "max_tokens": payload.max_tokens,
            "temperature": payload.temperature
        }
        resposta = cliente.enviar("completions", dados=dados)
        texto = resposta["choices"][0]["text"].strip()
        return CompletionResponse(response=texto)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def handle_list_models() -> ModelListResponse:
    try:
        cliente = ClienteHttpOpenAI()
        resposta = cliente.obter("models")
        modelos = [m["id"] for m in resposta.get("data", [])]
        return ModelListResponse(models=modelos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def handle_get_config() -> ConfigResponse:
    try:
        config = Config.get_instance()
        return ConfigResponse(config={k: v for k, v in vars(config).items() if not k.startswith('_')})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
