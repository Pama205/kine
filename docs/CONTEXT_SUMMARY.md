# kine — Development Context & Golden Rules

Quick reference for contributors and agents. When in doubt, default to the rules below.

---

## 1. Pydantic Is Required for All Public Data Structures

**Rule:** Every request, response, config object, or DTO that crosses a public boundary must be a `pydantic.BaseModel`.

### Why

Pydantic gives us runtime validation, JSON serialization, and excellent IDE autocompletion. It is the only heavyweight-ish dependency we accept in the core runtime.

### Current models

```python
# src/kine/schemas/requests.py
from pydantic import BaseModel

class TextGenerationRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 300

# src/kine/schemas/responses.py
from pydantic import BaseModel

class TextGenerationResponse(BaseModel):
    text: str
    model: str
    is_cached: bool = False
```

### Consequences

- No plain `dict` or `TypedDict` for public inputs/outputs.
- Validation errors are raised automatically before reaching business logic.
- Future providers can reuse the same domain models.

---

## 2. Mocking Is Required for Tests

**Rule:** Unit tests must never call real external APIs. Every test that exercises the engine or an adapter must use mocks, fakes, or stubs.

### Why

Real API calls are slow, flaky, require secrets, and cost money. They are integration concerns, not unit-test concerns.

### How to mock

#### Engine-level test

```python
import pytest
from unittest.mock import AsyncMock
from kine import Kine
from kine.schemas.requests import TextGenerationRequest
from kine.schemas.responses import TextGenerationResponse

@pytest.mark.asyncio
async def test_generate_text_delegates_to_provider():
    provider = AsyncMock()
    provider.generate_text.return_value = TextGenerationResponse(
        text="hello", model="mock"
    )

    ai = Kine(provider)
    result = await ai.generate_text("Hi")

    assert result.text == "hello"
    provider.generate_text.assert_awaited_once()
```

#### Adapter-level test

```python
import pytest
from unittest.mock import AsyncMock, patch
from kine.providers.gemini import GeminiProvider

@pytest.mark.asyncio
async def test_gemini_adapter_handles_api_error():
    provider = GeminiProvider(api_key="fake")
    # Patch the underlying SDK client
    with patch.object(provider, "_client") as mock_client:
        mock_client.generate_content.side_effect = RuntimeError("API down")
        ...
```

### Consequences

- `tests/` must run in CI without any `.env` file.
- Existing live-API scripts under `examples/` and `tests/unit/test_providers/test_gemini.py` are **not** valid unit tests. They will be replaced with mocked tests during the refactoring phase.

---

## 3. Environment Secrets Stay Outside the Library

**Rule:** `kine` reads configuration from constructor arguments or from environment variables loaded by the application. The library itself does not call `load_dotenv()` at import time.

### Correct pattern

```python
# Application code
from dotenv import load_dotenv
import os

load_dotenv()  # caller's responsibility
provider = GeminiProvider(api_key=os.getenv("GEMINI_API_KEY"))
```

### Anti-pattern (to be removed)

```python
# Inside an adapter module
from dotenv import load_dotenv
load_dotenv()  # side effect at import time
```

---

## 4. Provider SDKs Are Optional Extras

**Rule:** Installing `kine` alone must not install OpenAI, Gemini, or HuggingFace SDKs. Each provider is an optional extra.

```bash
poetry install --extras "gemini"      # only Gemini SDK
poetry install --extras "openai"      # only OpenAI SDK + httpx
poetry install --extras "all"         # all providers
```

### Why

Keeps the core library ultralight. Users pay only for the dependencies they use.

---

## 5. Type Safety Is Non-Negotiable

**Rule:** All public functions, methods, and class attributes must have strict type hints. `mypy --strict` must pass for the `src/` tree.

### Forbidden

```python
def __init__(self, api_key: str = None):  # implicit Optional
```

### Required

```python
from typing import Optional

def __init__(self, api_key: Optional[str] = None) -> None:
```

---

## Quick Checklist Before Submitting

- [ ] No `import` of third-party SDKs inside `src/kine/core.py` or `src/kine/schemas/`.
- [ ] All public I/O methods are `async def`.
- [ ] All public DTOs inherit from `pydantic.BaseModel`.
- [ ] Tests use `AsyncMock` or fakes; no real API calls.
- [ ] `poetry run mypy src` passes.
- [ ] `poetry run black --check src tests` passes.
- [ ] `poetry run isort --check-only src tests` passes.
