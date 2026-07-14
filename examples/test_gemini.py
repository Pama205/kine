import asyncio
from kine import Kine
from kine.providers.gemini import GeminiProvider
from kine.schemas.requests import TextGenerationRequest
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
api_model = "gemini-1.5-pro-latest"

provider = GeminiProvider(api_key=api_key, model=api_model)
kine = Kine(provider)


async def main() -> None:
    request = TextGenerationRequest(
        prompt="Explain string theory in one sentence",
        temperature=0.5,
        max_tokens=100,
    )
    response = await kine.generate_text(request)
    print("Response:", response.text)


asyncio.run(main())
