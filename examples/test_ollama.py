import asyncio
import time
from kine import Kine
from kine.providers.ollama import OllamaProvider


async def main() -> None:
    print("Starting Kine engine...")

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="qwen2.5-coder:3b",
    )

    engine = Kine(provider=provider)

    prompt = "Write a brief Python function to add two numbers."
    print(f"Sending prompt to qwen2.5-coder:3b...\n> '{prompt}'\n")

    try:
        start_time = time.perf_counter()
        response = await engine.generate_text(prompt)
        elapsed_time = time.perf_counter() - start_time

        print("-" * 40)
        print("RESPONSE:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        print(f"Response time: {elapsed_time:.2f}s")
        print(f"Model: {response.model}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("\nClosing connections...")
        await provider.aclose()


if __name__ == "__main__":
    asyncio.run(main())
