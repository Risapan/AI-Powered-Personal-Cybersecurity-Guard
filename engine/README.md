# friday-engine

The Python part of Friday: URL checks, risk scoring, storage, and the adapters for the local AI and the optional reputation lookups. See [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Setup

```sh
cd engine
uv sync            # creates .venv and installs the dev tools from uv.lock
```

## Checks

```sh
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
```
