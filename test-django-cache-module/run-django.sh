#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

pkill redis-server || true
sleep 1
rm -rf dump.rdb
redis-server --daemonize yes

cd mysite && uv run mprof run --multiprocess --output "../mprofile_$(date +%Y%m%d%H%M%S).dat" gunicorn wsgi && cd ..
