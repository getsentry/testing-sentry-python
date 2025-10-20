#!/bin/bash

# Install dependencies
uv sync

# Run the MCP server
uv run python main.py

