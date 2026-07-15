# kine — Unified AI Model Integration

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Poetry](https://img.shields.io/badge/packaging-poetry-cyan)

A Python library for integrating multiple AI providers (Gemini, OpenAI, DeepSeek, HuggingFace, etc.) through a simple, unified, async-first interface.

## Features

- **Multi-provider support:** Gemini, OpenAI, DeepSeek, HuggingFace, and more to come
- **Unified interface:** same methods for every provider
- **Strong typing:** automatic input/output validation with Pydantic
- **Easy to extend:** add new providers in minutes

## Installation

```bash
# With Poetry (recommended)
poetry install --extras "all"

# Or with pip
pip install kine[all]
```

## Project Structure

```plaintext
kine/
├── src/kine/              # Main package (src layout)
│   ├── __init__.py        # Public API exports
│   ├── core.py            # Kine entry point
│   ├── providers/         # Provider adapters
│   ├── schemas/           # Pydantic models
│   └── utils/             # Helpers
├── tests/                 # Unit tests (outside src/)
├── examples/              # Usage examples
├── docs/                  # Documentation
├── pyproject.toml         # Build configuration (Poetry)
├── README.md              # Main documentation
└── LICENSE                # MIT
```

## Quickstart

### With Ollama (default, no API key required)

```python
import asyncio
from kine import Kine
from kine.providers.ollama import OllamaProvider

async def main() -> None:
    provider = OllamaProvider()
    kine = Kine(provider)
    response = await kine.generate_text("Explain quantum computing in one sentence")
    print(response.text)

asyncio.run(main())
```

### With Gemini

```python
import asyncio
from kine import Kine
from kine.providers.gemini import GeminiProvider

async def main() -> None:
    provider = GeminiProvider(api_key="YOUR_API_KEY")
    kine = Kine(provider)
    response = await kine.generate_text("Explain quantum computing in one sentence")
    print(response.text)

asyncio.run(main())
```

> **Note:** **Ollama** is the default provider for development and works locally with no API key. Gemini, OpenAI, DeepSeek, and HuggingFace adapters are also available.

## Development

1. Clone the repository:

```bash
git clone https://github.com/your-user/kine.git
cd kine
```

2. Install in editable mode with all extras:

```bash
poetry install --extras "all"
```

3. Run tests:

```bash
poetry run pytest -v
```

## Contributing

Contributions are welcome. Please follow these steps:

1. Open an issue to discuss the change
2. Fork the project
3. Create a feature branch (`git checkout -b feature/awesome-feature`)
4. Commit your changes (`git commit -m 'Add awesome feature'`)
5. Push the branch (`git push origin feature/awesome-feature`)
6. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version details.

## Contact

- **Author:** Pedro A. Martínez A.
- **Email:** pama205@gmail.com
- **GitHub:** [@pama205](https://github.com/pama205)
