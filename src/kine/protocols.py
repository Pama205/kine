from typing import Protocol

from .schemas.requests import TextGenerationRequest
from .schemas.responses import TextGenerationResponse


class IAProvider(Protocol):
    async def generate_text(
        self, request: TextGenerationRequest
    ) -> TextGenerationResponse: ...

    async def generate_embeddings(self, text: str) -> list[float]: ...
