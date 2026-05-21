#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

rm -rf lambda_function_package.zip
rm -rf ./python_with_sentry/package/*

uv pip install --target ./python_with_sentry/package -r pyproject.toml

cd ./python_with_sentry/package && zip -x "**/__pycache__/*" -r ../../lambda_function_package.zip . && cd -

cd ./python_with_sentry && zip -g ../lambda_function_package.zip lambda_function.py && cd -
