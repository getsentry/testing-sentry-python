#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

cd mysite

uv run ./manage.py migrate

uv run ./manage.py runserver 0.0.0.0:8000
