# kine/schemas/requests.py
from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 300
