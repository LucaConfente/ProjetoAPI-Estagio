from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
from uweb_interface.backend.schemas import ChatRequest, ChatResponse, CompletionRequest, CompletionResponse, ModelListResponse, ConfigResponse
from src.chat import ChatModule
from src.http_client import ClienteHttpOpenAI
from src.config import Config

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTENTICAÇÃO ---
security = HTTPBearer()
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "API_LUCA")

def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != API_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- ROTAS ---

@app.get("/")
def root():
    return {"message": "API rodando! Veja /docs para documentação."}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/auth-check", dependencies=[Depends(authenticate)])
def auth_check():
    return {"detail": "Autorização concedida!"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
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

@app.post("/completions", response_model=CompletionResponse, dependencies=[Depends(authenticate)])
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=ModelListResponse, dependencies=[Depends(authenticate)])
def list_models():
    try:
        cliente = ClienteHttpOpenAI()
        resposta = cliente.obter("models")
        modelos = [m["id"] for m in resposta.get("data", [])]
        return ModelListResponse(models=modelos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config", response_model=ConfigResponse, dependencies=[Depends(authenticate)])
def get_config():
    try:
        config = Config.get_instance()
        return ConfigResponse(config={k: v for k, v in vars(config).items() if not k.startswith('_')})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
