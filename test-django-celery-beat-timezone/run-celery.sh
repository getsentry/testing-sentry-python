#!/usr/bin/env bash
set -euo pipefail

reset

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

redis-server --daemonize yes

cd mysite

uv run celery -A mysite.tasks.app worker \
    --loglevel=DEBUG \
    -B \
    -c 1 \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
