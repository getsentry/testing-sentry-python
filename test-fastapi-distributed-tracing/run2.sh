#!/usr/bin/env bash
set -euo pipefail
reset

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv run uvicorn main2:app --port 5002 --reload
