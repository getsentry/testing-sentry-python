#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

rm -f celerybeat-schedule
rm -rf dump.rdb

redis-server --daemonize yes

uv run celery -A tasks.app worker \
    --concurrency=1 \
    --max-tasks-per-child=1
