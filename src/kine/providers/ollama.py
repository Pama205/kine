from typing import cast

import httpx

from ..errors import ProviderAPIError
from ..schemas.requests import TextGenerationRequest
from ..schemas.responses import TextGenerationResponse


class OllamaProvider:
    def __init__(
        self,
        model: str = "llama3.2:1b",
        base_url: str = "http://localhost:11434",
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=60.0)

    async def generate_text(
        self, request: TextGenerationRequest
    ) -> TextGenerationResponse:
        payload = {
            "model": self._model,
            "prompt": request.prompt,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
            "stream": False,
        }
        try:
            resp = await self._client.post(
                f"{self._base_url}/api/generate", json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return TextGenerationResponse(text=data["response"], model=self._model)
        except httpx.HTTPError as e:
            raise ProviderAPIError(f"Ollama API error: {e}") from e

    async def generate_embeddings(self, text: str) -> list[float]:
        payload = {"model": self._model, "prompt": text}
        try:
            resp = await self._client.post(
                f"{self._base_url}/api/embeddings", json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return cast(list[float], data["embedding"])
        except httpx.HTTPError as e:
            raise ProviderAPIError(f"Ollama embedding error: {e}") from e
