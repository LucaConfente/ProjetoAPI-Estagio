import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uweb_interface.backend.schemas import ChatRequest, ChatResponse, CompletionRequest, CompletionResponse, ModelListResponse, ConfigResponse
from uweb_interface.backend.controllers import handle_chat, handle_completions, handle_list_models, handle_get_config

router = APIRouter()

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

@router.get("/")
def root():
    return {"message": "API rodando! Veja /docs para documentação."}


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/auth-check", dependencies=[Depends(authenticate)])
def auth_check():
    return {"detail": "Autorização concedida!"}


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    return handle_chat(payload)


@router.post("/completions", response_model=CompletionResponse, dependencies=[Depends(authenticate)])
def completions_endpoint(payload: CompletionRequest):
    return handle_completions(payload)


@router.get("/models", response_model=ModelListResponse, dependencies=[Depends(authenticate)])
def list_models():
    return handle_list_models()


@router.get("/config", response_model=ConfigResponse, dependencies=[Depends(authenticate)])
def get_config():
    return handle_get_config()
