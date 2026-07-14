# kine/schemas/responses.py
from pydantic import BaseModel


class TextGenerationResponse(BaseModel):
    text: str
    model: str
    is_cached: bool = False
