
from fastapi import FastAPI, HTTPException
from uweb_interface.backend.schemas import ChatRequest, ChatResponse, CompletionRequest, CompletionResponse, ModelListResponse, ConfigResponse
from src.chat import ChatModule
from src.http_client import ClienteHttpOpenAI
from src.config import Config


app = FastAPI()


# Endpoint raiz para evitar 404 e orientar o usuário
@app.get("/")
def root():
    return {"message": "API rodando! Veja /docs para documentação ou /health para status."}
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/completions", response_model=CompletionResponse)
def completions_endpoint(payload: CompletionRequest):
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=ModelListResponse)
def list_models():
    try:
        cliente = ClienteHttpOpenAI()
        resposta = cliente.obter("models")
        modelos = [m["id"] for m in resposta.get("data", [])]
        return ModelListResponse(models=modelos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config", response_model=ConfigResponse)
def get_config():
    try:
        config = Config.get_instance()
        return ConfigResponse(config={k: v for k, v in vars(config).items() if not k.startswith('_')})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    try:
        chat_module = ChatModule()
        
        mensagens = [m.dict() for m in payload.messages]
        resposta = chat_module.criar_conversa(mensagens=mensagens, modelo=payload.model)
        conteudo = resposta["choices"][0]["message"]["content"].strip()
        return ChatResponse(response=conteudo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
