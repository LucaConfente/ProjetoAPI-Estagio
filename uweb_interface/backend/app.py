# Endpoint para checar autenticação
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
from uweb_interface.backend.schemas import ChatRequest, ChatResponse, CompletionRequest, CompletionResponse, ModelListResponse, ConfigResponse
from src.chat import ChatModule
from src.http_client import ClienteHttpOpenAI
from src.config import Config


app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para produção, troque '*' pelo domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Autenticação Bearer Token ---
security = HTTPBearer()
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "API_AUTH_TOKEN")  # Defina no .env para produção

def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != API_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/auth-check", dependencies=[Depends(authenticate)])
def auth_check():
    return {"detail": "Autorização concedida!"}

# Endpoint raiz para evitar 404 e orientar o usuário
@app.get("/")
def root():
    return {"message": "API rodando! Veja /docs para documentação ou /health para status."}
@app.get("/health")
def health_check():
    return {"status": "ok"}

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

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(authenticate)])
def chat_endpoint(payload: ChatRequest):
    try:
        chat_module = ChatModule()
        
        mensagens = [m.dict() for m in payload.messages]
        resposta = chat_module.criar_conversa(mensagens=mensagens, modelo=payload.model)
        conteudo = resposta["choices"][0]["message"]["content"].strip()
        return ChatResponse(response=conteudo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
