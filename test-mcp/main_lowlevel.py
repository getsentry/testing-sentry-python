#!/usr/bin/env python3
"""
Example MCP server using the low-level mcp.server.lowlevel API with Sentry integration.

This demonstrates the low-level API which provides more control compared to FastMCP.

Key differences from FastMCP:
- Manual tool/resource/prompt listing
- More verbose setup
- More control over server behavior
- Direct access to MCP protocol details
"""

import os
import asyncio
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.mcp import MCPIntegration

from mcp.server.lowlevel import Server
from mcp.server import stdio
from mcp.types import (
    Tool,
    Resource,
    Prompt,
    TextContent,
    GetPromptResult,
    PromptMessage,
    CallToolResult,
)


# Initialize Sentry
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test-lowlevel"),
    traces_sample_rate=1.0,
    send_default_pii=True,
    debug=True,
    integrations=[MCPIntegration()],
)


# Create the low-level MCP server
server = Server("example-lowlevel-server")


# ============================================================================
# TOOL HANDLERS
# ============================================================================
# Tools must be explicitly listed in list_tools handler
# and implemented as call_tool handlers


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="calculate_sum",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="calculate_product",
            description="Multiply two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="greet_user",
            description="Generate a personalized greeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User's name"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="trigger_error",
            description="Trigger an error to test Sentry integration",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool execution based on tool name."""
    
    if name == "calculate_sum":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return [TextContent(type="text", text=f"The sum of {a} and {b} is {result}")]
    
    elif name == "calculate_product":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a * b
        return [TextContent(type="text", text=f"The product of {a} and {b} is {result}")]
    
    elif name == "greet_user":
        name_arg = arguments.get("name", "stranger")
        greeting = f"Hello, {name_arg}! Welcome to the low-level MCP server."
        return [TextContent(type="text", text=greeting)]
    
    elif name == "trigger_error":
        raise ValueError("This is a test error to verify Sentry is working!")
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ============================================================================
# RESOURCE HANDLERS
# ============================================================================
# Resources must be explicitly listed in list_resources handler
# and implemented as read_resource handlers


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List all available resources."""
    return [
        Resource(
            uri="config://settings",
            name="Server Settings",
            description="Server configuration settings",
            mimeType="text/plain",
        ),
        Resource(
            uri="data://users",
            name="User List",
            description="List of sample users",
            mimeType="text/plain",
        ),
        Resource(
            uri="data://stats",
            name="Server Statistics",
            description="Server runtime statistics",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Handle resource reading based on URI."""
    
    if uri == "config://settings":
        return """Server Configuration:
- Version: 1.0.0
- Environment: Development
- Max Connections: 100
- Timeout: 30s
"""
    
    elif uri == "data://users":
        return """Users:
1. Alice (admin@example.com)
2. Bob (bob@example.com)
3. Charlie (charlie@example.com)
4. Diana (diana@example.com)
"""
    
    elif uri == "data://stats":
        import json
        stats = {
            "uptime": "1h 23m",
            "requests": 42,
            "errors": 0,
            "memory_usage": "125 MB"
        }
        return json.dumps(stats, indent=2)
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


# ============================================================================
# PROMPT HANDLERS
# ============================================================================
# Prompts must be explicitly listed in list_prompts handler
# and implemented as get_prompt handlers


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available prompts."""
    return [
        Prompt(
            name="code_review",
            description="Generate a code review prompt",
            arguments=[
                {
                    "name": "language",
                    "description": "Programming language",
                    "required": False,
                }
            ],
        ),
        Prompt(
            name="debug_assistant",
            description="Generate a debugging assistant prompt",
            arguments=[],
        ),
        Prompt(
            name="sql_query_helper",
            description="Help write SQL queries",
            arguments=[
                {
                    "name": "database_type",
                    "description": "Type of database (postgres, mysql, etc.)",
                    "required": False,
                }
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, Any] | None) -> GetPromptResult:
    """Handle prompt retrieval based on prompt name."""
    
    if name == "code_review":
        language = arguments.get("language", "python") if arguments else "python"
        prompt_text = f"""You are an expert {language} code reviewer. Please review the following code and provide:

1. Code quality assessment
2. Potential bugs or issues
3. Performance improvements
4. Best practices recommendations
5. Security considerations

Be specific and constructive in your feedback."""
        
        return GetPromptResult(
            description=f"Code review prompt for {language}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )
    
    elif name == "debug_assistant":
        prompt_text = """You are a debugging assistant. Help the user:

1. Understand the error message
2. Identify the root cause
3. Suggest potential fixes
4. Provide prevention strategies

Ask clarifying questions if needed."""
        
        return GetPromptResult(
            description="Debugging assistant prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )
    
    elif name == "sql_query_helper":
        db_type = arguments.get("database_type", "PostgreSQL") if arguments else "PostgreSQL"
        prompt_text = f"""You are an expert {db_type} database engineer. Help the user:

1. Write efficient SQL queries
2. Optimize existing queries
3. Explain query execution plans
4. Follow {db_type} best practices
5. Ensure proper indexing

Provide clear explanations and examples."""
        
        return GetPromptResult(
            description=f"SQL query helper for {db_type}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text),
                )
            ],
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")


# ============================================================================
# SERVER LIFECYCLE
# ============================================================================


async def main():
    """Run the MCP server using stdio transport."""
    async with stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

