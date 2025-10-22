#!/bin/bash

# Install dependencies
uv sync

# Run the MCP server + the mcp inspector
uv run mcp dev main.py
