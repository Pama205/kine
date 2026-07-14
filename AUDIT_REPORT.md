# Architecture Audit Report — kine

**Scope:** Orthogonality, adapter isolation, concurrency, DX/public API, and packaging.
**Auditor:** OpenCode (strict mode)
**Date:** 2026-07-14

---

## Executive Summary

The repository is in a very early, partially implemented state. Only the **Gemini** provider works; OpenAI, DeepSeek, and HuggingFace adapters are empty stubs. The current architecture violates the core requirement that the domain engine must depend on abstractions, not concrete implementations. The single implemented adapter is not isolated, the public API is incomplete, the code is fully synchronous, and the packaging layout does not follow modern `src/` conventions.

**Overall verdict:** The library does **not** comply with the stated architecture standards. Significant refactoring is required before it can be considered production-grade or "ultralight."

---

## 1. Orthogonality and Contract Verification (Domain Layer)

### Standard
The core engine must depend only on domain contracts (`typing.Protocol` or `ABC`), never on concrete third-party libraries, SDKs, or I/O details.

### Findings

#### 1.1 No domain protocol/ABC for providers exists
`kine/core.py` references providers only through dynamic string imports and duck typing. There is no `Protocol` or `ABC` defining what a provider must implement.

```python
# kine/core.py
PROVIDERS = {
    'gemini': ('kine.providers.gemini', 'GeminiProvider')
}

def _load_provider(self, provider_name: str, config: Dict) -> Type:
    module_path, class_name = self.PROVIDERS[provider_name]
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)(**config)
```

The engine calls `self.provider.generate_text(prompt)` blindly. Any object with that method will work, but there is no contract enforced by type checkers or runtime checks.

#### 1.2 The engine reads environment variables directly
`core.py` imports `os` and resolves API keys from the environment. Key resolution is an infrastructure concern and should not live in the domain engine.

```python
# kine/core.py
import os

api_key = config.get('api_key') or os.getenv(f"{provider_name.upper()}_API_KEY")
if not api_key:
    raise APIKeyNotFoundError(f"API key no proporcionada para {provider_name}")
```

#### 1.3 Concrete schema classes are imported into the engine
While not as severe as importing an SDK, the engine hardcodes `TextGenerationRequest` and `TextGenerationResponse`. A cleaner design would define domain-level request/response protocols so the engine remains agnostic of specific DTO shapes.

### Severity
**High** — the engine is coupled to concrete provider resolution and environment handling.

### Recommended Fixes

1. Define a `Protocol` in a new `kine/domain/protocols.py`:

```python
from typing import Protocol
from kine.schemas.requests import TextGenerationRequest
from kine.schemas.responses import TextGenerationResponse

class IAProvider(Protocol):
    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        ...
```

2. Make `Kine` accept an injected provider instance or a factory that returns `IAProvider`:

```python
class Kine:
    def __init__(self, provider: IAProvider) -> None:
        self.provider = provider
```

3. Move API-key resolution and module loading to an adapter factory/registry (`kine/providers/factory.py`), not `core.py`.

---

## 2. Infrastructure Isolation Verification (Adapters)

### Standard
Adapters must implement the domain protocol exactly and encapsulate all external I/O, HTTP handling, JSON parsing, and SDK-specific errors. No infrastructure exceptions should leak to the engine.

### Findings

#### 2.1 Adapter does not implement a declared protocol
`kine/providers/gemini.py` defines `GeminiProvider` as a plain class. It does not explicitly implement any domain protocol.

```python
# kine/providers/gemini.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class GeminiProvider:
    ...
```

#### 2.2 Adapter imports infrastructure directly
The adapter imports `google.generativeai`, configures the API key, and instantiates `genai.GenerativeModel` directly. This is correct **only if** the class is hidden behind a protocol, but currently the engine knows only the concrete class name via string import.

```python
# kine/providers/gemini.py
genai.configure(api_key=api_key)
self.model = genai.GenerativeModel(model)
```

#### 2.3 Error handling is too broad and leaks SDK exceptions
The adapter catches `Exception` generically and re-raises a class defined locally (`GeminiAPIError`), which is itself defined inside the adapter file rather than in the shared `errors.py` module.

```python
# kine/providers/gemini.py
except Exception as e:
    raise GeminiAPIError(f"Error en Gemini: {str(e)}")

class GeminiAPIError(Exception):
    """Error específico de la API de Gemini."""
    pass
```

This means:
- The engine cannot catch a unified domain exception.
- Stack traces from the Google SDK are stringified and may lose machine-readable details.
- `GeminiAPIError` is not exported from the package.

#### 2.4 Response metadata is hardcoded and incorrect
The adapter returns `model="gemini-pro"` regardless of the model actually used.

```python
# kine/providers/gemini.py
return TextGenerationResponse(
    text=response.text,
    model="gemini-pro"
)
```

#### 2.5 Empty infrastructure modules
`kine/utils/cache.py`, `logger.py`, and `safety.py` are empty. The spec mentions caching, logging, and safety filters, but no infrastructure exists for them.

### Severity
**High** — the single working adapter mixes SDK, configuration, and error concerns without a domain contract.

### Recommended Fixes

1. Implement adapters against `IAProvider`:

```python
class GeminiProvider:
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest") -> None:
        ...

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        ...
```

2. Translate SDK exceptions into domain exceptions defined in `kine/errors.py`:

```python
class ProviderAPIError(KineError):
    """Raised when an external provider API call fails."""
```

3. Return the real model name and capture usage metadata.
4. Remove `load_dotenv()` from the adapter; environment loading should happen once at application startup.

---

## 3. Performance and Concurrency Verification

### Standard
All network-bound and I/O-bound methods must be `async` and use async HTTP clients (`httpx`, `aiohttp`) so the library can be used in FastAPI/Starlette without blocking the event loop.

### Findings

#### 3.1 The entire public API is synchronous
`Kine.__init__` and `Kine.generate_text` are `def`, not `async def`. The provider method is also synchronous.

```python
# kine/core.py
def generate_text(self, prompt: str | TextGenerationRequest, **kwargs) -> TextGenerationResponse:
    ...

# kine/providers/gemini.py
def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
    response = self.model.generate_content(...)
```

#### 3.2 The adapter uses a blocking SDK
`google-generativeai` is a synchronous SDK. Calling `self.model.generate_content(...)` blocks the thread for the entire HTTP round-trip.

```python
# kine/providers/gemini.py
response = self.model.generate_content(
    contents=request.prompt,
    generation_config={...}
)
```

#### 3.3 `requests` is listed as a core dependency
`pyproject.toml` includes `requests = "^2.31.0"` as a non-optional dependency, even though no code currently uses it. This signals intent to use synchronous HTTP elsewhere.

```toml
# pyproject.toml
requests = "^2.31.0"
```

### Severity
**Critical** — the library cannot be used safely in async server environments without blocking the event loop.

### Recommended Fixes

1. Convert the domain protocol and all public methods to `async`:

```python
class IAProvider(Protocol):
    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        ...

class Kine:
    async def generate_text(self, prompt: str | TextGenerationRequest, **kwargs) -> TextGenerationResponse:
        ...
```

2. Use an async HTTP client for providers that expose REST endpoints. For SDKs without async support, run the call in a `ThreadPoolExecutor` and expose it as `async`:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class GeminiProvider:
    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gemini_")

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._sync_generate_text,
            request,
        )
```

3. Replace `requests` with `httpx` and make it optional per-provider.

---

## 4. Developer Experience (DX) and Public API Verification

### Standard
A developer should install the package and use it with minimal code and perfect autocompletion. Public types must be strict and fully exported via `__init__.py`.

### Findings

#### 4.1 Public exports are incomplete
`kine/__init__.py` only exports `Kine`, `KineError`, and `ProviderNotFoundError`. It omits the request/response schemas and other exceptions (`APIKeyNotFoundError`, `APIModelNotFoundError`), forcing users to import from internal modules.

```python
# kine/__init__.py
from .core import Kine
from .errors import KineError, ProviderNotFoundError

__all__ = ["Kine", "KineError", "ProviderNotFoundError"]
```

#### 4.2 Constructor accepts invalid typing
`Kine.__init__` declares `api_key: str = None`, which is a mypy error (PEP 484 prohibits implicit Optional).

```python
# kine/core.py
def __init__(self, provider: str = "gemini", api_key: str = None, model: str = None, **kwargs):
```

#### 4.3 `_load_provider` return type is wrong
The method is annotated `-> Type` but returns an instance. With no protocol, mypy cannot verify the result.

```python
# kine/core.py
def _load_provider(self, provider_name: str, config: Dict) -> Type:
    ...
    return getattr(module, class_name)(**config)
```

#### 4.4 No static provider discovery
Because the provider is selected by string (`"gemini"`), IDEs cannot autocomplete available providers or their configurations.

#### 4.5 5-line script simulation
This is the minimal happy-path script today:

```python
from kine import Kine
from kine.schemas.requests import TextGenerationRequest  # internal import

ai = Kine("gemini")
request = TextGenerationRequest(prompt="Hello", temperature=0.5)
response = ai.generate_text(request)
print(response.text)
```

Problems:
- `TextGenerationRequest` is not exported from the top-level package.
- It requires a `GEMINI_API_KEY` environment variable or an `api_key=` argument.
- It is synchronous, so it is unsuitable for async frameworks.

### Severity
**Medium-High** — the API is usable but incomplete, poorly typed, and not async-friendly.

### Recommended Fixes

1. Export schemas and all public exceptions from `__init__.py`:

```python
# kine/__init__.py
from .core import Kine
from .errors import KineError, ProviderNotFoundError, APIKeyNotFoundError, APIModelNotFoundError
from .schemas.requests import TextGenerationRequest
from .schemas.responses import TextGenerationResponse

__all__ = [
    "Kine",
    "KineError",
    "ProviderNotFoundError",
    "APIKeyNotFoundError",
    "APIModelNotFoundError",
    "TextGenerationRequest",
    "TextGenerationResponse",
]
```

2. Fix type hints:

```python
def __init__(
    self,
    provider: str = "gemini",
    api_key: str | None = None,
    model: str | None = None,
    **kwargs: Any,
) -> None:
```

3. Provide explicit provider constructors so users can write:

```python
from kine import Kine
from kine.providers import GeminiProvider

ai = Kine(GeminiProvider(api_key="..."))
response = await ai.generate_text("Hello")
```

---

## 5. Project Structure and Package Management Verification

### Standard
Use a modern `src/` layout, keep tests outside `src/`, keep core dependencies minimal, declare all runtime dependencies explicitly, and separate dev tools into `[tool.poetry.group.dev.dependencies]`.

### Findings

#### 5.1 No `src/` layout
The package `kine/` lives directly in the repository root. Modern Python packaging recommends `src/kine/` to prevent accidental imports from the working directory and to ensure the installed package is tested, not the source tree.

```text
kine/
├── kine/          # <- should be src/kine/
├── tests/
└── pyproject.toml
```

#### 5.2 `pydantic` is used but not declared
`kine/schemas/requests.py` and `responses.py` import `pydantic`, but `pydantic` is not listed in `[tool.poetry.dependencies]`. It is currently installed only as a transitive dependency of other packages.

```python
# kine/schemas/requests.py
from pydantic import BaseModel
```

```toml
# pyproject.toml — pydantic is missing here
[tool.poetry.dependencies]
python = "^3.10"
openai = { version = "^1.0", optional = true }
google-generativeai = { version = "^0.3.0", optional = true }
huggingface-hub = { version = "^0.20.0", optional = true }
requests = "^2.31.0"
rich = "^13.7.0"
python-dotenv = "^1.0.0"
```

#### 5.3 Heavy dependencies are not optional
`requests` and `rich` are listed as mandatory core dependencies. For an "ultralight" multi-provider library, these should be optional or removed.

#### 5.4 Broken `deepseek` extra
The `deepseek` extra references `"deepseek"`, but the dependency itself is commented out and no such PyPI package exists.

```toml
# pyproject.toml
dependencies:
  # deepseek = { version = "^0.0.1", optional = true }

[tool.poetry.extras]
deepseek = ["deepseek"]
all = ["openai", "huggingface-hub", "google-generativeai", "deepseek"]
```

Installing with `--extras "all"` currently works only because the line is commented out and Poetry ignores it; otherwise it would fail.

#### 5.5 Dev dependencies are correctly grouped
`pytest`, `mypy`, `black`, `isort`, `pre-commit`, and `git-changelog` are correctly placed under `[tool.poetry.group.dev.dependencies]`. This part complies with the standard.

#### 5.6 No tool configuration
There are no `[tool.black]`, `[tool.isort]`, `[tool.mypy]`, or `[tool.pytest.ini_options]` sections. As a result:
- `pytest` collects `test_*.py` from the entire repo, including `examples/`.
- `mypy` runs with defaults that reject implicit Optional.
- `black` and `isort` use their own defaults, which currently report many issues.

### Severity
**High** — missing dependency declaration, broken extra, and non-standard layout are all packaging risks.

### Recommended Fixes

1. Migrate to `src/` layout and update `pyproject.toml`:

```toml
packages = [{include = "kine", from = "src"}]
```

2. Declare `pydantic` explicitly and move heavy deps to optional extras:

```toml
[tool.poetry.dependencies]
python = "^3.10"
pydantic = "^2.5"
python-dotenv = { version = "^1.0.0", optional = true }

openai = { version = "^1.0", optional = true }
google-generativeai = { version = "^0.3.0", optional = true }
huggingface-hub = { version = "^0.20.0", optional = true }
httpx = { version = "^0.27", optional = true }

[tool.poetry.extras]
gemini = ["google-generativeai"]
openai = ["openai", "httpx"]
huggingface = ["huggingface-hub", "httpx"]
all = ["google-generativeai", "openai", "huggingface-hub", "httpx", "python-dotenv"]
```

3. Remove the `deepseek` extra until a real dependency exists.
4. Add tool configurations:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 88
```

---

## Action Priority

| Priority | Item | Category |
|---|---|---|
| Critical | Convert public API and adapters to `async` | Concurrency |
| Critical | Define and use `IAProvider` protocol | Domain / Adapters |
| High | Move provider loading and env-var resolution out of `core.py` | Domain |
| High | Declare `pydantic` and make heavy deps optional | Packaging |
| High | Migrate to `src/` layout | Packaging |
| High | Translate SDK exceptions into domain exceptions | Adapters |
| Medium | Export schemas and exceptions from `__init__.py` | DX |
| Medium | Fix mypy type errors (`str = None`, `-> Type`) | DX |
| Medium | Remove or implement empty stubs (`cache.py`, `logger.py`, `safety.py`, provider stubs) | Completeness |
| Low | Add `[tool.*]` configurations for black, isort, mypy, pytest | Tooling |

---

*End of audit report.*
