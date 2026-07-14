from typing import Any

from .protocols import IAProvider
from .schemas.requests import TextGenerationRequest
from .schemas.responses import TextGenerationResponse


class Kine:
    def __init__(self, provider: IAProvider) -> None:
        self._provider = provider

    async def generate_text(
        self, prompt: str | TextGenerationRequest, **kwargs: Any
    ) -> TextGenerationResponse:
        if isinstance(prompt, TextGenerationRequest):
            return await self._provider.generate_text(prompt)
        request = TextGenerationRequest(prompt=prompt, **kwargs)
        return await self._provider.generate_text(request)

    async def generate_embeddings(self, text: str) -> list[float]:
        return await self._provider.generate_embeddings(text)
