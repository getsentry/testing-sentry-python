#!/usr/bin/env python3
"""
Example MCP server using mcp.fastmcp with Sentry integration.

This demonstrates:
- Tools: Functions that can be called by the client
- Resources: Data that can be accessed by the client
- Prompts: Pre-defined prompt templates
"""
import os
import sys
import sentry_sdk
from sentry_sdk.integrations.mcp import MCPIntegration

from fastmcp import FastMCP, Context

from pydantic import BaseModel, Field
from typing import List


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test-sync"),
    traces_sample_rate=1.0,
    send_default_pii=True,
    debug=True,
    integrations=[MCPIntegration()],
)

# Create the MCP server
mcp = FastMCP("Example MCP Server")


# Define Pydantic models for structured output
class TextStatistics(BaseModel):
    """Statistics about a text string."""
    character_count: int = Field(description="Total number of characters")
    word_count: int = Field(description="Total number of words")
    line_count: int = Field(description="Total number of lines")
    sentence_count: int = Field(description="Approximate number of sentences")
    average_word_length: float = Field(description="Average length of words")
    longest_word: str = Field(description="The longest word in the text")
    shortest_word: str = Field(description="The shortest word in the text")


class UserInfo(BaseModel):
    """User information structure."""
    id: int = Field(description="User ID")
    name: str = Field(description="User name")
    email: str = Field(description="User email")
    role: str = Field(description="User role")
    active: bool = Field(description="Whether the user is active")


class UserList(BaseModel):
    """List of users with metadata."""
    total: int = Field(description="Total number of users")
    users: List[UserInfo] = Field(description="List of user objects")


# Define a tool - these are functions the client can call
@mcp.tool()
async def calculate_sum(a: int, b: int, ctx: Context) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
async def calculate_sum_no_context(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def calculate_product(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b


@mcp.tool()
def greet_user(name: str) -> str:
    """Generate a personalized greeting."""
    return f"Hello, {name}! Welcome to the MCP server."


@mcp.tool()
def trigger_error() -> str:
    """Trigger an error to test Sentry integration."""
    raise ValueError("This is a test error to verify Sentry is working!")


@mcp.tool()
def analyze_text(text: str) -> TextStatistics:
    """Analyze text and return structured statistics.
    
    This demonstrates structured output using a Pydantic model.
    """
    import re
    
    # Calculate character count
    character_count = len(text)
    
    # Calculate line count
    lines = text.split('\n')
    line_count = len(lines)
    
    # Calculate word count and word-related statistics
    words = text.split()
    word_count = len(words)
    
    # Filter out words that are only punctuation
    actual_words = [word.strip('.,!?;:()[]{}"\'-') for word in words]
    actual_words = [word for word in actual_words if word]
    
    if actual_words:
        average_word_length = sum(len(word) for word in actual_words) / len(actual_words)
        longest_word = max(actual_words, key=len)
        shortest_word = min(actual_words, key=len)
    else:
        average_word_length = 0.0
        longest_word = ""
        shortest_word = ""
    
    # Calculate sentence count (approximate)
    sentence_endings = re.findall(r'[.!?]+', text)
    sentence_count = len(sentence_endings) if sentence_endings else 1
    
    return TextStatistics(
        character_count=character_count,
        word_count=word_count,
        line_count=line_count,
        sentence_count=sentence_count,
        average_word_length=round(average_word_length, 2),
        longest_word=longest_word,
        shortest_word=shortest_word,
    )


@mcp.tool()
def get_user_list(include_inactive: bool = False) -> UserList:
    """Get a list of users with structured information.
    
    This demonstrates structured output with nested Pydantic models.
    """
    all_users = [
        UserInfo(id=1, name="Alice Smith", email="alice@example.com", role="admin", active=True),
        UserInfo(id=2, name="Bob Johnson", email="bob@example.com", role="user", active=True),
        UserInfo(id=3, name="Charlie Brown", email="charlie@example.com", role="user", active=True),
        UserInfo(id=4, name="Diana Prince", email="diana@example.com", role="moderator", active=False),
        UserInfo(id=5, name="Eve Davis", email="eve@example.com", role="user", active=False),
    ]
    
    if include_inactive:
        filtered_users = all_users
    else:
        filtered_users = [user for user in all_users if user.active]
    
    return UserList(
        total=len(filtered_users),
        users=filtered_users,
    )


# Define resources - these provide access to data
@mcp.resource("config://settings")
def get_settings() -> str:
    """Get server configuration settings."""
    return """
Server Configuration:
- Version: 1.0.0
- Environment: Development
- Max Connections: 100
"""


@mcp.resource("data://users")
def get_users() -> str:
    """Get a list of sample users."""
    return """
Users:
1. Alice (admin@example.com)
2. Bob (bob@example.com)
3. Charlie (charlie@example.com)
"""


# Define prompts - these are reusable prompt templates
@mcp.prompt()
def code_review_prompt(language: str = "python") -> str:
    """Generate a code review prompt for a specific language."""
    return f"""You are an expert {language} code reviewer. Please review the following code and provide:

1. Code quality assessment
2. Potential bugs or issues
3. Performance improvements
4. Best practices recommendations
5. Security considerations

Be specific and constructive in your feedback."""


@mcp.prompt()
def debug_assistant_prompt() -> str:
    """Generate a debugging assistant prompt."""
    return """You are a debugging assistant. Help the user:

1. Understand the error message
2. Identify the root cause
3. Suggest potential fixes
4. Provide prevention strategies

Ask clarifying questions if needed."""


import uvicorn
from starlette.middleware.cors import CORSMiddleware
# from mcp.server.fastmcp import FastMCP


if __name__ == "__main__":
    # Get the Starlette app for streamable HTTP
    starlette_app = mcp.streamable_http_app()

    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Run the server
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)