# AGENTS.md — kine

Compact, repo-specific notes for OpenCode sessions.

## Project basics

- Python 3.10+ package managed with **Poetry**. Run everything via `poetry run ...`.
- Source layout: package lives under `src/kine/`. Public API is exported from `src/kine/__init__.py` (`Kine`, `KineError`, `ProviderNotFoundError`, `ProviderAPIError`, `IAProvider`).
- Entry point class: `kine.core:Kine`. Constructor receives an `IAProvider`-conforming instance (dependency injection).
- Domain contract: `src/kine/protocols.py` defines `IAProvider` (Protocol) with `async generate_text()` and `async generate_embeddings()`.

## Setup

```bash
poetry install --extras "all"
```

- **Ollama** (default for dev) and **Gemini** providers are implemented.
- `OllamaProvider` talks to `http://localhost:11434` (no API key needed).
- `GeminiProvider` requires `GEMINI_API_KEY`.
- `src/kine/providers/openai.py`, `deepseek.py`, and `huggingface.py` are placeholder stubs with implementation notes.
- `deepseek` extra was removed because there is no official PyPI package.
- `src/kine/schemas/requests.py` and `responses.py` use **Pydantic**.

## Environment / API keys

- Providers expect keys via `.env` (loaded with `python-dotenv`) or passed as `api_key=`.
- `.env.example` defines: `GEMINI_API_KEY`, `CHATGPT_API_KEY`, `DEEPSEEK_API_KEY`, `HF_TOKEN`.
- Ollama needs no key; Gemini consumes `GEMINI_API_KEY`.

## Testing

```bash
poetry run pytest -v
```

- Test configuration in `pyproject.toml` under `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `asyncio_mode = "auto"`).
- Existing "tests" are live integration scripts; they make real API calls. Need mocked unit tests.
- `tests/unit/test_core.py`, `test_chatgpt.py`, and `test_deepseek.py` are empty files.

## Lint / typecheck / format

All pass on `src/`:

- `poetry run black --check src tests`
- `poetry run isort --check-only src tests`
- `poetry run mypy src`

## Changelog

- Generated via `git-changelog` using `poetry run changelog` (configured as a Poetry script in `pyproject.toml`).
- Implementation in `scripts/generate_changelog.py`.

## Documentation

- Architecture and context docs: `docs/ARCHITECTURE.md`, `docs/CONTEXT_SUMMARY.md`.
- `docs/DEVELOPMENT.md`, `docs/PROVIDERS.md`, `docs/ADVANCED.md`, and `docs/api-reference.md` are currently empty.
- Non-empty docs: `README.md`, `docs/QUICKSTART.md`, `docs/KINE_SPEC.md`, `docs/ARCHITECTURE.md`, `docs/CONTEXT_SUMMARY.md`, `CHANGELOG.md`.

## Notable repo state

- No CI workflows, no pre-commit config, no `opencode.json`, no existing agent instruction files.
- This is a very early-stage repo; several files are placeholders.
- A `.gitignore` file is now present.
