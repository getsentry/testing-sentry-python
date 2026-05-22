#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

rm -f celerybeat-schedule
rm -rf dump.rdb

redis-server --daemonize yes

uv run celery -A main.app worker \
    --loglevel=DEBUG \
    --concurrency=1
