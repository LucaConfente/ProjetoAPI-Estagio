from pydantic import BaseModel

class ChatResponse(BaseModel):
    response: str
from typing import List, Optional, Any, Dict

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-3.5-turbo"


class CompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = "text-davinci-003"
    max_tokens: Optional[int] = 128
    temperature: Optional[float] = 0.7

class CompletionResponse(BaseModel):
    response: str

class ModelListResponse(BaseModel):
    models: list[str]

class ConfigResponse(BaseModel):
    config: Dict[str, Any]
