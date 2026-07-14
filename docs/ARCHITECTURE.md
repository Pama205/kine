# kine — Architecture Decision Record

This document is the single source of truth for the structural and design principles of the `kine` library. Every contribution must respect the three pillars below.

---

## 1. Async-Only Public API

**Rule:** All I/O-bound operations exposed by `kine` must be `async def`. No blocking network calls may leak out of the library.

### Why

`kine` is designed to be embedded in modern Python backends (FastAPI, Starlette, Sanic, async task workers). A synchronous call to an external LLM API blocks the event loop and degrades throughput.

### Consequences

- The facade `Kine.generate_text` and every adapter method are `async`.
- Adapters use async HTTP clients (`httpx.AsyncClient`) when a REST API is available.
- If a provider SDK is synchronous (e.g., `google-generativeai`), the adapter runs the SDK call inside a `ThreadPoolExecutor` and exposes it as `async`. The caller never sees sync code.

```python
# Correct usage inside an async framework
response = await ai.generate_text("Explain quantum computing")
```

---

## 2. Dependency Injection via Protocols

**Rule:** The domain core depends on abstractions, never on concrete implementations. Adapters are injected, not imported by name inside the engine.

### Structure

```text
src/kine/
├── __init__.py         # public API exports
├── core.py             # Kine facade / orchestration
├── errors.py           # framework-agnostic exception hierarchy
├── providers/          # concrete adapter implementations
├── schemas/            # request/response Pydantic models
└── utils/              # caching, logging, safety helpers
```

### Dependency direction

Dependencies point inward:

- `core.py` and `schemas/` import **nothing** from concrete provider modules.
- Provider modules import from `schemas/` and `errors/`.
- User/application code imports from the public API (`kine`) or from explicit provider modules.

### Example

```python
# kine/core.py
from typing import Protocol
from kine.schemas.requests import TextGenerationRequest
from kine.schemas.responses import TextGenerationResponse

class IAProvider(Protocol):
    async def generate_text(
        self, request: TextGenerationRequest
    ) -> TextGenerationResponse: ...

class Kine:
    def __init__(self, provider: IAProvider) -> None:
        self._provider = provider

    async def generate_text(
        self, prompt: str | TextGenerationRequest, **kwargs
    ) -> TextGenerationResponse:
        ...
```

### Consequences

- `Kine` does not know whether the provider is Gemini, OpenAI, or a mock.
- Adapters are interchangeable at runtime.
- Unit tests inject `AsyncMock` objects instead of calling real APIs.

---

## 3. Core Decoupling from Infrastructure

**Rule:** The engine must not import third-party SDKs, HTTP clients, databases, or environment variables directly.

### Forbidden in `core.py` and `schemas/`

- `import google.generativeai`
- `import openai`
- `import httpx` (only allowed inside adapters)
- `import os` for API-key resolution
- `load_dotenv()` calls
- Framework-specific exceptions (`fastapi.HTTPException`, etc.)

### Allowed in the core

- Pure Python standard library (`typing`, `abc`, `dataclasses`, `enum`, etc.)
- Domain models and protocols defined inside `kine`

### Configuration flow

1. The application layer (user code) reads environment variables or config files.
2. A factory/registry builds the concrete adapter with the resolved configuration.
3. The adapter instance is injected into `Kine`.

```python
# User/application code — not inside kine
from kine import Kine
from kine.providers.gemini import GeminiProvider

provider = GeminiProvider(api_key="...")
ai = Kine(provider)

response = await ai.generate_text("Hello")
```

---

## Current Implementation Status

The codebase is being refactored toward the architecture above. As of the latest audit:

- Only the **Gemini** provider is fully implemented.
- `OpenAI`, `DeepSeek`, and `HuggingFace` adapters are placeholder stubs.
- The public API, provider discovery, and error hierarchy are still being aligned with the rules in this document.

See `AUDIT_REPORT.md` for the full gap analysis and remediation plan.

---

## Summary

| Principle | Decision |
|---|---|
| Concurrency | **Async-only** public API |
| Coupling | **Injected protocols**, no direct SDK imports in core |
| Architecture | **Clean/Hexagonal**: domain schemas and facade at the center, adapters at the edge |

Any change that violates these principles must be rejected or refactored before merging.
