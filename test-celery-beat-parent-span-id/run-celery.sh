#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

redis-server --daemonize yes

uv run celery -A tasks.app worker \
    --loglevel=INFO \
    -c 1
