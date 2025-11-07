#!/usr/bin/env bash

# Install uv if it's not installed
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Run the truncation test script
export SENTRY_SPOTLIGHT=1
uv run python main_truncation.py




