#!/usr/bin/env bash
set -e

# Install dependencies (sentry-python is mounted as a volume at /sentry-python)
uv sync --no-dev

# Start the app
uv run uvicorn main:app --host 0.0.0.0 --port 5000
