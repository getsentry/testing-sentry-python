#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

redis-server --daemonize yes

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

uv run celery -A tasks.app worker \
    --loglevel=DEBUG \
    -B \
    -c 1 \
    --max-tasks-per-child 10000
