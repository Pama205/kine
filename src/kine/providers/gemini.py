import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import google.generativeai as genai

from ..errors import APIKeyNotFoundError, ProviderAPIError
from ..schemas.requests import TextGenerationRequest
from ..schemas.responses import TextGenerationResponse


class GeminiProvider:
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest") -> None:
        if not api_key:
            raise APIKeyNotFoundError("API key is required for Gemini")
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(model)
        except Exception as e:
            raise ProviderAPIError(f"Gemini initialization failed: {e}") from e
        self._model_name = model
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gemini_")

    async def generate_text(
        self, request: TextGenerationRequest
    ) -> TextGenerationResponse:
        try:
            response = await asyncio.to_thread(self._sync_generate, request)
            return TextGenerationResponse(text=response.text, model=self._model_name)
        except Exception as e:
            raise ProviderAPIError(f"Gemini API error: {e}") from e

    def _sync_generate(self, request: TextGenerationRequest) -> Any:
        return self._model.generate_content(
            contents=request.prompt,
            generation_config={
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
            },
        )

    async def generate_embeddings(self, text: str) -> list[float]:
        raise ProviderAPIError("Embeddings are not supported by Gemini provider")

    async def aclose(self) -> None:
        self._executor.shutdown(wait=True)

    async def __aenter__(self) -> "GeminiProvider":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
