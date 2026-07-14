import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import google.generativeai as genai

from ..errors import APIKeyNotFoundError, ProviderAPIError
from ..schemas.requests import TextGenerationRequest
from ..schemas.responses import TextGenerationResponse


class GeminiProvider:
    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gemini_")

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest") -> None:
        if not api_key:
            raise APIKeyNotFoundError("API key is required for Gemini")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._model_name = model

    async def generate_text(
        self, request: TextGenerationRequest
    ) -> TextGenerationResponse:
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                self._executor,
                self._sync_generate,
                request,
            )
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
        raise NotImplementedError("Embeddings not yet supported for Gemini")
