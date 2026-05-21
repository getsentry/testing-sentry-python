#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if [ ! -d ".venv" ]; then
    uv venv
fi

source .venv/bin/activate
uv pip install -e .

python main.py
