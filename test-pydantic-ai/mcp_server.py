#!/usr/bin/env python3
"""Simple MCP server with basic tools."""

from mcp.server.fastmcp import FastMCP

app = FastMCP("SimpleCalculator")


@app.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@app.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b


@app.tool()
def get_word_count(text: str) -> int:
    """Count the number of words in a text string."""
    return len(text.split())


if __name__ == "__main__":
    app.run(transport="stdio")

