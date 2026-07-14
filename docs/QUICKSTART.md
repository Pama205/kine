# Quickstart

## 1. Install

Use Poetry with all provider extras:

```bash
poetry install --extras "all"
```

Or install only the provider you need:

```bash
poetry install --extras "gemini"
```

## 2. Basic Usage

The public API is async-first. Use `await` inside an async context:

```python
import asyncio
from kine import Kine
from kine.providers.gemini import GeminiProvider
from kine.schemas.requests import TextGenerationRequest

async def main() -> None:
    provider = GeminiProvider(api_key="YOUR_API_KEY")
    ai = Kine(provider)

    request = TextGenerationRequest(prompt="Hello", temperature=0.5)
    response = await ai.generate_text(request)
    print(response.text)

asyncio.run(main())
```

You can also pass a plain prompt string:

```python
response = await ai.generate_text("Explain quantum computing in one sentence")
```

## 3. Run Tests

```bash
poetry run pytest -v
```

> **Note:** The current test files under `tests/` are live integration scripts that require a valid `GEMINI_API_KEY`. A mocking refactor is in progress so the suite can run in CI without secrets.
