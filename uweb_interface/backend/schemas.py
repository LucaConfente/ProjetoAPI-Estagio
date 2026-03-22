from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ChatResponse(BaseModel):
    response: str

class Message(BaseModel):
    role: str
    content: str

class FilePayload(BaseModel):
    type: str        # 'image' ou 'text'
    name: str
    mime: str
    data: str        # base64 para imagens, texto puro para arquivos de texto

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-3.5-turbo"
    files: Optional[List[FilePayload]] = []

class CompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-3.5-turbo-instruct"
    max_tokens: Optional[int] = 128
    temperature: Optional[float] = 0.7

class CompletionResponse(BaseModel):
    response: str

class ModelListResponse(BaseModel):
    models: list[str]

class ConfigResponse(BaseModel):
    config: Dict[str, Any]
