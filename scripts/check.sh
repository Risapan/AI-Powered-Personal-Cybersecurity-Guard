#!/bin/sh
# Run every check in the repo. Stops at the first failure.
set -eu
cd "$(git rev-parse --show-toplevel)"

echo "==> Secret scan (gitleaks)"
gitleaks git --redact --no-banner --config .gitleaks.toml

echo "==> Engine (Python)"
(
  cd engine
  uv sync --quiet
  uv run ruff format --check .
  uv run ruff check .
  uv run mypy
  uv run pytest -q
)

echo "==> Extension (TypeScript)"
(
  cd extension
  npm ci --silent
  npm run --silent check
)

echo "All checks passed."
