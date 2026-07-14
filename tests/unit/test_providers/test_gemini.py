import asyncio

from kine import Kine
from kine.providers.gemini import GeminiProvider
from kine.schemas.requests import TextGenerationRequest

provider = GeminiProvider(api_key="test-key")
kine = Kine(provider)


async def main() -> None:
    request = TextGenerationRequest(prompt="Translate: Hello world", temperature=0.5)
    response = await kine.generate_text(request)
    print(response.text)


asyncio.run(main())
