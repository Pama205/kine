# Architecture Audit Report — kine

**Scope:** Orthogonality, adapter isolation, concurrency, DX/public API, and packaging.
**Auditor:** OpenCode (Strict Mode)
**Date:** 2026-07-15

---

## Executive Summary

The `kine` library has made significant progress toward Clean Architecture since the previous audit. The core (`Kine`) no longer imports SDKs, resolves environment variables, or manages a provider registry. The `IAProvider` protocol is defined, and both `OllamaProvider` and `GeminiProvider` conform structurally.

However, several critical and high-severity issues remain — including resource leaks in adapters, unexported public types, a mandatory runtime dependency that violates separation of concerns, and the complete absence of both unit tests and CI pipeline.

**Overall verdict:** The architecture direction is correct, but production-readiness requires fixing 2 critical, 4 high, and 4 medium issues before a 1.0 release.

---

## 1. Orthogonality and Contract Verification (Domain Layer)

### Standard
The domain engine must depend only on domain contracts (`typing.Protocol` or ABCs), never on concrete third-party libraries, SDKs, or I/O details.

### Findings

#### 1.1 Protocol defined — but uses absolute imports

`IAProvider` is defined in `src/kine/protocols.py` using the correct `typing.Protocol` base. However, it uses absolute imports (`from kine.schemas.request import ...`) instead of relative imports:

```python
# src/kine/protocols.py:3-4
from kine.schemas.requests import TextGenerationRequest   # absolute
from kine.schemas.responses import TextGenerationResponse  # absolute
```

Absolute imports make the module fragile when the package is installed in a non-standard layout or when running tests outside the installed environment. Relative imports (`from ..schemas.requests import ...`) are the convention within a single package.

**Severity:** Medium  
**Fix:** Switch to relative imports:

```python
from ..schemas.requests import TextGenerationRequest
from ..schemas.responses import TextGenerationResponse
```

#### 1.2 Protocol imports concrete DTOs

`IAProvider` directly references `TextGenerationRequest` and `TextGenerationResponse`. In strict Clean Architecture, the domain protocol should define its own abstract request/response types to avoid coupling to Pydantic. However, for a library of this size, using Pydantic models as domain types is a pragmatic trade-off.

**Severity:** Low (informational)  

#### 1.3 `Kine.generate_text` bypasses type safety with `**kwargs`

```python
# src/kine/core.py:12-18
async def generate_text(
    self, prompt: str | TextGenerationRequest, **kwargs: Any
) -> TextGenerationResponse:
```

`**kwargs: Any` disables autocomplete and type checking for `temperature`, `max_tokens`, and any future request fields. The caller gets no IDE feedback.

**Severity:** Medium  
**Fix:** Accept an optional `TextGenerationRequest` or make the constructor parameters explicit:

```python
async def generate_text(
    self,
    prompt: str | TextGenerationRequest,
    temperature: float = 0.7,
    max_tokens: int = 300,
) -> TextGenerationResponse:
    if isinstance(prompt, TextGenerationRequest):
        request = prompt
    else:
        request = TextGenerationRequest(
            prompt=prompt, temperature=temperature, max_tokens=max_tokens
        )
    return await self._provider.generate_text(request)
```

### Domain Verdict
| # | Issue | Severity |
|---|---|---|
| 1.1 | Absolute imports in `protocols.py` | Medium |
| 1.2 | Protocol imports concrete DTOs | Low |
| 1.3 | `**kwargs: Any` disables type safety | Medium |

---

## 2. Infrastructure Isolation Verification (Adapters)

### Standard
Adapters must implement the domain protocol exactly and encapsulate all external I/O, HTTP handling, SDK errors, and configuration. No raw SDK exceptions may leak to callers.

### Findings

#### 2.1 `GeminiProvider.__init__` leaks SDK exceptions (CRITICAL)

```python
# src/kine/providers/gemini.py:18-19
genai.configure(api_key=api_key)
self._model = genai.GenerativeModel(model)
```

Both `genai.configure()` and `genai.GenerativeModel()` can raise `google.api_core.exceptions.*` (e.g., `InvalidArgument`, `PermissionDenied`). These are NOT caught by any try/except block, so they propagate unmodified to the caller. A user of `GeminiProvider` could receive a raw Google SDK exception.

**Severity:** Critical  
**Fix:** Wrap initialization in a try/except that maps to `ProviderAPIError`:

```python
def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest") -> None:
    if not api_key:
        raise APIKeyNotFoundError("API key is required for Gemini")
    try:
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._model_name = model
    except Exception as e:
        raise ProviderAPIError(f"Gemini initialization failed: {e}") from e
```

#### 2.2 `GeminiProvider` class-level `ThreadPoolExecutor` never shut down (HIGH)

```python
# src/kine/providers/gemini.py:13
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gemini_")
```

This executor is created at class definition time and **never shut down**. A `ThreadPoolExecutor` that is not explicitly shut down keeps worker threads alive until the interpreter exits. If providers are created/destroyed dynamically (e.g., in a web server worker), threads accumulate.

**Severity:** High  
**Fix:** Make the executor an instance attribute and provide a shutdown method or use `AsyncExitStack`:

```python
def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest") -> None:
    ...
    self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gemini_")

async def shutdown(self) -> None:
    self._executor.shutdown(wait=True)
```

Alternatively, implement `__del__` or an async context manager.

#### 2.3 `OllamaProvider` `AsyncClient` never closed (HIGH)

```python
# src/kine/providers/ollama.py:18
self._client = httpx.AsyncClient(timeout=60.0)
```

The `httpx.AsyncClient` is created in `__init__` but never closed. The `httpx` documentation explicitly warns that unclosed clients can leak connections and file descriptors.

**Severity:** High  
**Fix:** Implement an async teardown method or use the client as a context manager:

```python
async def shutdown(self) -> None:
    await self._client.aclose()
```

#### 2.4 `GeminiProvider` raises `NotImplementedError` for embeddings (MEDIUM)

```python
async def generate_embeddings(self, text: str) -> list[float]:
    raise NotImplementedError("Embeddings not yet supported for Gemini")
```

`NotImplementedError` is a raw Python exception, not part of the `KineError` hierarchy. A caller doing `except KineError` will not catch this.

**Severity:** Medium  
**Fix:** Use `ProviderAPIError` instead:

```python
async def generate_embeddings(self, text: str) -> list[float]:
    raise ProviderAPIError("Embeddings are not supported by Gemini provider")
```

#### 2.5 Placeholder stubs with correct docstrings exist — no code

`openai.py`, `deepseek.py`, `huggingface.py` remain placeholder stubs with no implementation.

**Severity:** Low (expected for early-stage)

### Adapter Verdict
| # | Issue | Severity |
|---|---|---|
| 2.1 | `GeminiProvider.__init__` leaks SDK exceptions | **Critical** |
| 2.2 | `ThreadPoolExecutor` never shut down | High |
| 2.3 | `AsyncClient` never closed | High |
| 2.4 | `NotImplementedError` outside error hierarchy | Medium |
| 2.5 | Placeholder stubs | Low |

---

## 3. Performance and Concurrency Verification

### Standard
All network-bound and I/O-bound methods must be `async def`. Blocking SDK calls must be wrapped with `run_in_executor` or `to_thread`. Async HTTP clients (e.g., `httpx.AsyncClient`) must be used for REST-based adapters.

### Findings

#### 3.1 Public API is async — conformant

`Kine.generate_text`, `Kine.generate_embeddings`, `OllamaProvider.generate_text`, `OllamaProvider.generate_embeddings`, and `GeminiProvider.generate_text` are all `async def`. Gemini wraps its sync SDK via `run_in_executor`. This satisfies the standard.

**Severity:** None (pass)

#### 3.2 `asyncio.get_event_loop()` is the deprecated path (MEDIUM)

```python
# src/kine/providers/gemini.py:25-28
loop = asyncio.get_event_loop()
response = await loop.run_in_executor(
    self._executor,
    self._sync_generate,
    request,
)
```

`asyncio.get_event_loop()` is deprecated in Python 3.12 when there is no running loop. The modern replacement is `asyncio.to_thread()`, available since Python 3.9:

**Severity:** Medium  
**Fix:**

```python
async def generate_text(
    self, request: TextGenerationRequest
) -> TextGenerationResponse:
    try:
        response = await asyncio.to_thread(self._sync_generate, request)
        return TextGenerationResponse(text=response.text, model=self._model_name)
    except Exception as e:
        raise ProviderAPIError(f"Gemini API error: {e}") from e
```

#### 3.3 No async lifecycle management (MEDIUM)

Neither `OllamaProvider` nor `GeminiProvider` implements an async teardown method or context manager (`__aenter__`/`__aexit__`). Users have no standard way to release client connections and executor threads.

**Severity:** Medium  
**Fix:** Add an `aclose()` method and consider implementing the async context manager protocol:

```python
class OllamaProvider:
    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
```

### Concurrency Verdict
| # | Issue | Severity |
|---|---|---|
| 3.1 | Public API is async | Clear |
| 3.2 | `get_event_loop()` deprecated path | Medium |
| 3.3 | No async lifecycle management | Medium |

---

## 4. Developer Experience and Public API Verification

### Standard
A developer must install the package and use it with minimal code and perfect autocompletion. Public types must have strict type hints and be fully exported via `__init__.py`.

### Findings

#### 4.1 `TextGenerationRequest` and `TextGenerationResponse` not exported (HIGH)

```python
from kine import Kine, KineError  # works
from kine.schemas.requests import TextGenerationRequest  # required, not top-level
```

`TextGenerationRequest` and `TextGenerationResponse` are referenced in the protocol and in `Kine.generate_text`, but are missing from `__init__.py` exports. Users must either import from `kine.schemas.requests` (violating encapsulation) or construct the request inline via `**kwargs`.

**Severity:** High  
**Fix:** Add them to `__init__.py`:

```python
from .schemas.requests import TextGenerationRequest
from .schemas.responses import TextGenerationResponse

__all__ = [
    "Kine",
    "KineError",
    "ProviderAPIError",
    "ProviderNotFoundError",
    "IAProvider",
    "TextGenerationRequest",
    "TextGenerationResponse",
]
```

#### 4.2 `APIKeyNotFoundError` and `APIModelNotFoundError` not exported (MEDIUM)

These exceptions exist in `errors.py` (used by `GeminiProvider.__init__`) but are not exported from `__init__.py`. Callers cannot catch them without deep imports.

**Severity:** Medium  
**Fix:** Export them alongside `ProviderAPIError`:

```python
from .errors import KineError, ProviderAPIError, ProviderNotFoundError, APIKeyNotFoundError, APIModelNotFoundError

__all__ = [
    # ...,
    "APIKeyNotFoundError",
    "APIModelNotFoundError",
]
```

#### 4.3 `Kine.generate_text` has no docstrings (LOW)

```python
# src/kine/core.py:12-18
async def generate_text(
    self, prompt: str | TextGenerationRequest, **kwargs: Any
) -> TextGenerationResponse:
```

Users get no inline help in their IDE. A clear docstring describing the two calling conventions (string + kwargs vs. explicit `TextGenerationRequest`) would significantly improve DX.

**Severity:** Low  
**Fix:** Add docstrings:

```python
async def generate_text(
    self, prompt: str | TextGenerationRequest, **kwargs: Any
) -> TextGenerationResponse:
    """Generate text using the configured provider.

    Two calling conventions:
        1. await kine.generate_text("Explain quantum computing")
        2. await kine.generate_text(TextGenerationRequest(prompt="..."))

    Args:
        prompt: Plain string or pre-built TextGenerationRequest.
        **kwargs: Overrides for temperature, max_tokens (only when prompt is a string).

    Returns:
        TextGenerationResponse with generated text and metadata.
    """
```

### DX Verdict
| # | Issue | Severity |
|---|---|---|
| 4.1 | `TextGenerationRequest`/`TextGenerationResponse` not exported | **High** |
| 4.2 | `APIKeyNotFoundError`/`APIModelNotFoundError` not exported | Medium |
| 4.3 | No docstrings on `Kine` methods | Low |

---

## 5. Project Structure and Package Management Verification

### Standard
Use a modern `src/` layout with `tests/`, `docs/`, `examples/` in the root. Heavy dependencies must be optional (`extras`). Tool configurations for pytest, mypy, black, isort must be explicit.

### Findings

#### 5.1 `python-dotenv` is a mandatory core dependency (HIGH)

```toml
# pyproject.toml:15
python-dotenv = "^1.0.0"
```

`python-dotenv` is listed as a mandatory runtime dependency. The core library (`Kine`) no longer calls `load_dotenv()` or imports `dotenv` anywhere. The only remaining usage is in `examples/test_gemini.py` and `tests/unit/test_providers/test_gemini.py` — both user/application code, not library code. This dependency adds unnecessary weight to every installation.

**Severity:** High  
**Fix:** Move `python-dotenv` to optional extras or development dependencies:

```toml
# Remove from [tool.poetry.dependencies]
# Option A: make it optional
python-dotenv = { version = "^1.0.0", optional = true }

# Option B: move to dev (if only used in examples/tests)
# Remove entirely from [tool.poetry.dependencies]
[tool.poetry.group.dev.dependencies]
python-dotenv = "^1.0.0"
```

#### 5.2 `pyproject.toml` changelog sections in Spanish (MEDIUM)

```toml
[tool.git-changelog]
sections = [
    { name = "feat", title = "🚀 Nuevas Funcionalidades" },
    { name = "fix", title = "🐛 Correcciones" },
    { name = "perf", title = "⚡ Mejoras de Rendimiento" },
    { name = "refactor", title = "♻️ Refactorizaciones" }
]
```

The section titles are in Spanish. For a library with an English README, docs, and error messages, the changelog configuration should also be in English.

**Severity:** Medium  
**Fix:**

```toml
[tool.git-changelog]
sections = [
    { name = "feat", title = "🚀 Features" },
    { name = "fix", title = "🐛 Bug Fixes" },
    { name = "perf", title = "⚡ Performance Improvements" },
    { name = "refactor", title = "♻️ Refactoring" }
]
```

#### 5.3 No CI workflow (HIGH)

The repository has no `.github/workflows/` directory. For a PyPI-targeted library in 2026, a CI pipeline that runs `pytest`, `mypy`, `black`, and `isort` on every push and PR is a baseline expectation.

**Severity:** High  
**Fix:** Add a minimal GitHub Actions workflow:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install poetry
      - run: poetry install --extras all
      - run: poetry run mypy src
      - run: poetry run black --check src tests
      - run: poetry run isort --check-only src tests
```

#### 5.4 Tests are live integration scripts, not unit tests (MEDIUM)

All files under `tests/` are either empty (`test_core.py`, `test_chatgpt.py`, `test_deepseek.py`) or execute real API calls (`test_gemini.py` calls Gemini with a fake key, which will fail at runtime). There are no mocked unit tests.

**Severity:** Medium  
**Fix:** Write proper unit tests with `AsyncMock`:

```python
# tests/unit/test_core.py
import pytest
from unittest.mock import AsyncMock
from kine import Kine
from kine.schemas.requests import TextGenerationRequest
from kine.schemas.responses import TextGenerationResponse

@pytest.mark.asyncio
async def test_generate_text_delegates_to_provider():
    provider = AsyncMock()
    provider.generate_text.return_value = TextGenerationResponse(
        text="hello", model="test"
    )
    kine = Kine(provider)
    result = await kine.generate_text("Hi")
    assert result.text == "hello"
    provider.generate_text.assert_awaited_once()
```

#### 5.5 `examples/basic_usage.py` is empty (LOW)

This file is supposed to be the first example a contributor reads, but it contains nothing.

**Severity:** Low  
**Fix:** Populate it with the same content as the Quickstart in `README.md`.

#### 5.6 `.env.example` includes keys for unimplemented providers (LOW)

`CHATGPT_API_KEY`, `DEEPSEEK_API_KEY`, and `HF_TOKEN` are listed but the corresponding providers are stubs. This misleads users.

**Severity:** Low  
**Fix:** Keep only `GEMINI_API_KEY` and add `OLLAMA_HOST` if needed:

```bash
GEMINI_API_KEY=your_key_here
```

### Packaging Verdict
| # | Issue | Severity |
|---|---|---|
| 5.1 | `python-dotenv` mandatory, unused in core | **High** |
| 5.2 | Changelog sections in Spanish | Medium |
| 5.3 | No CI workflow | **High** |
| 5.4 | Tests are live scripts, not unit tests | Medium |
| 5.5 | `examples/basic_usage.py` empty | Low |
| 5.6 | `.env.example` has keys for stubs | Low |

---

## Action Priority

| Priority | Item | Category |
|---|---|---|
| **Critical** | Wrap `GeminiProvider.__init__` SDK calls in try/except to prevent leaking raw SDK exceptions | Adapters |
| **High** | Shut down `ThreadPoolExecutor` in `GeminiProvider` | Adapters |
| **High** | Close `httpx.AsyncClient` in `OllamaProvider` | Adapters |
| **High** | Export `TextGenerationRequest`/`TextGenerationResponse` from `__init__.py` | DX |
| **High** | Remove `python-dotenv` from mandatory deps (make optional or dev-only) | Packaging |
| **High** | Add GitHub Actions CI workflow | Packaging |
| **Medium** | Replace `asyncio.get_event_loop()` with `asyncio.to_thread()` | Concurrency |
| **Medium** | Replace `NotImplementedError` with `ProviderAPIError` in Gemini embeddings | Adapters |
| **Medium** | Export `APIKeyNotFoundError`/`APIModelNotFoundError` from `__init__.py` | DX |
| **Medium** | Add async lifecycle (`aclose` / `__aexit__`) to both providers | Concurrency |
| **Medium** | Write mocked unit tests for `Kine` and adapters | Testing |
| **Medium** | Translate changelog sections to English | Packaging |
| **Medium** | Switch `protocols.py` to relative imports | Domain |
| **Medium** | Remove `**kwargs: Any` in favor of explicit parameters | Domain/DX |
| **Low** | Add docstrings to `Kine` methods | DX |
| **Low** | Populate `examples/basic_usage.py` | Documentation |
| **Low** | Clean up `.env.example` | Packaging |

---

## Summary

```
Pillar 1 — Domain:      2 Medium, 1 Low
Pillar 2 — Adapters:    1 Critical, 2 High, 1 Medium, 1 Low
Pillar 3 — Concurrency: 2 Medium
Pillar 4 — DX:          1 High, 1 Medium, 1 Low
Pillar 5 — Packaging:   2 High, 2 Medium, 2 Low
```

The architectural skeleton is sound. The `IAProvider` protocol and dependency injection in `Kine` are correct. The remaining work is completing the adapter lifecycle, cleaning up the dependency tree, building CI, and adding proper mocked tests.

*End of audit report.*
