#!/bin/bash

# Install dependencies
uv sync

# Run the low-level MCP server
uv run python main_lowlevel.py

