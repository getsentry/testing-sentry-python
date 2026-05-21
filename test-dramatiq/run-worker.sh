#!/usr/bin/env bash
set -euo pipefail
reset

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

pkill redis-server || true
sleep 1
rm -rf dump.rdb
redis-server --daemonize yes

uv run dramatiq --processes 1 main
