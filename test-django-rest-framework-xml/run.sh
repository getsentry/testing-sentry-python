#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

cd mysite

uv run daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
