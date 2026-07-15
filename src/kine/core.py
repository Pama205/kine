from .protocols import IAProvider
from .schemas.requests import TextGenerationRequest
from .schemas.responses import TextGenerationResponse


class Kine:
    """Main entry point for interacting with AI providers.

    Usage:
        kine = Kine(OllamaProvider())
        response = await kine.generate_text("Explain quantum computing")

    The provider is injected via dependency injection and must conform
    to the IAProvider protocol.
    """

    def __init__(self, provider: IAProvider) -> None:
        self._provider = provider

    async def generate_text(
        self,
        prompt: str | TextGenerationRequest,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> TextGenerationResponse:
        """Generate text using the configured provider.

        Two calling conventions:
            1.  await kine.generate_text("Explain quantum computing")
            2.  request = TextGenerationRequest(prompt="...", temperature=0.5)
                await kine.generate_text(request)

        Args:
            prompt: Plain string prompt or a pre-built TextGenerationRequest.
            temperature: Sampling temperature (0.0-2.0). Only used when
                prompt is a string. Ignored when passing a TextGenerationRequest.
            max_tokens: Maximum tokens in the response. Only used when
                prompt is a string. Ignored when passing a TextGenerationRequest.

        Returns:
            TextGenerationResponse containing the generated text and metadata.
        """
        if isinstance(prompt, TextGenerationRequest):
            return await self._provider.generate_text(prompt)
        request = TextGenerationRequest(
            prompt=prompt, temperature=temperature, max_tokens=max_tokens
        )
        return await self._provider.generate_text(request)

    async def generate_embeddings(self, text: str) -> list[float]:
        """Generate embeddings for the given text using the configured provider.

        Args:
            text: Input text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        return await self._provider.generate_embeddings(text)
