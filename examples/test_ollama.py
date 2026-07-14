import asyncio
from kine import Kine
from kine.providers.ollama import OllamaProvider


async def main() -> None:
    provider = OllamaProvider()
    kine = Kine(provider)
    response = await kine.generate_text("Explain quantum computing in one sentence")
    print(response.text)


asyncio.run(main())
