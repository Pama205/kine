# Technical Specification: `kine` Library

## Goal

Build an open-source Python library that simplifies integration with multiple AI providers (Gemini, OpenAI, DeepSeek, HuggingFace, etc.) through a unified, async-first interface with:

- Text-generation and embedding models
- Automatic caching
- Strong typing and data validation
- Easy extension for new providers

## Project Structure

```plaintext
kine/
├── src/kine/                   # Source package (src layout)
│   ├── __init__.py             # Public API exports
│   ├── core.py                 # Main Kine class
│   ├── errors.py               # Custom exceptions
│   ├── providers/              # Provider adapters
│   │   ├── __init__.py
│   │   ├── gemini.py           # Implemented
│   │   ├── openai.py           # Placeholder stub
│   │   ├── deepseek.py         # Placeholder stub
│   │   └── huggingface.py      # Placeholder stub
│   ├── schemas/                # Pydantic data models
│   │   ├── requests.py
│   │   └── responses.py
│   └── utils/                  # Helpers
│       ├── cache.py            # Placeholder
│       ├── logger.py           # Placeholder
│       └── safety.py           # Placeholder
├── tests/                      # Tests outside src/
│   └── unit/
│       ├── test_core.py
│       └── test_providers/
│           ├── test_gemini.py
│           ├── test_chatgpt.py
│           └── test_deepseek.py
├── examples/                   # Usage examples
├── scripts/                    # Automation scripts
├── docs/                       # Documentation
├── pyproject.toml              # Poetry configuration
└── README.md
```

## Public API (Target)

```python
import asyncio
from kine import Kine
from kine.providers.gemini import GeminiProvider

async def main() -> None:
    provider = GeminiProvider(api_key="...")
    ai = Kine(provider)
    response = await ai.generate_text("Explain quantum computing in one sentence")
    print(response.text)

asyncio.run(main())
```

## Architecture Principles

1. **Async-only:** every I/O operation is `async`.
2. **Dependency injection:** the core receives adapters that satisfy a `Protocol`.
3. **Decoupling:** the domain layer does not import SDKs or make network calls.

For details, see `docs/ARCHITECTURE.md` and `docs/CONTEXT_SUMMARY.md`.

## Implementation Status

- **Gemini:** fully implemented (sync SDK wrapped to satisfy the async contract is the target).
- **OpenAI / DeepSeek / HuggingFace:** placeholder stubs with implementation notes.
- **Cache, logger, safety:** placeholder modules to be implemented.
- **Tests:** currently live integration scripts; mocking refactor is in progress per the architecture audit.
