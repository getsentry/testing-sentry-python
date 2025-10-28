#!/bin/bash

# Install dependencies
uv sync

# Run the MCP server
uv run fastmcp dev main_fastmcp.py

