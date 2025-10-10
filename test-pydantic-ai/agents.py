"""
Simple, focused agents for testing Pydantic AI integration with Sentry.
"""

from pydantic_ai import Agent
from pydantic import BaseModel


class CalculationResult(BaseModel):
    """Result from mathematical calculations."""
    result: int
    operation: str
    explanation: str


class AnalysisResult(BaseModel):
    """Result from data analysis."""
    summary: str
    key_findings: list[str]
    recommendation: str


# Simple agent without tools
simple_agent = Agent(
    "openai:gpt-4o-mini",
    name="simple_agent",
    instructions="You are a helpful assistant. Provide clear, concise answers.",
    model_settings={
        "temperature": 0.3,
        "max_tokens": 200,
    },
)


# Agent with mathematical tools
math_agent = Agent(
    "openai:gpt-4o-mini",
    name="math_agent",
    instructions="You are a mathematical assistant. Use the available tools to perform calculations and return structured results.",
    output_type=CalculationResult,
    model_settings={
        "temperature": 0.1,
        "max_tokens": 300,
    },
)


@math_agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@math_agent.tool_plain
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b


@math_agent.tool_plain
def calculate_percentage(part: float, total: float) -> float:
    """Calculate what percentage 'part' is of 'total'."""
    if total == 0:
        return 0.0
    return (part / total) * 100


# First agent in two-agent setup - data collector
data_collector_agent = Agent(
    "openai:gpt-4o-mini",
    name="data_collector",
    instructions="You collect and prepare data for analysis. Extract key numbers and organize information clearly.",
    model_settings={
        "temperature": 0.2,
        "max_tokens": 400,
    },
)


@data_collector_agent.tool_plain
def extract_numbers(text: str) -> list[int]:
    """Extract all numbers from a text string."""
    import re
    numbers = re.findall(r'\d+', text)
    return [int(n) for n in numbers]


@data_collector_agent.tool_plain
def organize_data(items: list[str]) -> dict:
    """Organize a list of items into categories."""
    return {
        "total_items": len(items),
        "items": items,
        "categories": list(set(item.split()[0] if item.split() else "unknown" for item in items))
    }


# Second agent in two-agent setup - data analyzer
data_analyzer_agent = Agent(
    "openai:gpt-4o-mini",
    name="data_analyzer",
    instructions="You analyze data provided by the data collector and provide insights and recommendations.",
    output_type=AnalysisResult,
    model_settings={
        "temperature": 0.4,
        "max_tokens": 500,
    },
)


@data_analyzer_agent.tool_plain
def calculate_statistics(numbers: list[int]) -> dict:
    """Calculate basic statistics for a list of numbers."""
    if not numbers:
        return {"error": "No numbers provided"}
    
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


@data_analyzer_agent.tool_plain
def identify_trends(numbers: list[int]) -> str:
    """Identify trends in a sequence of numbers."""
    if len(numbers) < 2:
        return "Not enough data to identify trends"
    
    differences = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
    
    if all(d > 0 for d in differences):
        return "Increasing trend"
    elif all(d < 0 for d in differences):
        return "Decreasing trend"
    elif all(d == 0 for d in differences):
        return "Constant values"
    else:
        return "Mixed trend"


# Anthropic agents for provider testing
anthropic_simple_agent = Agent(
    "anthropic:claude-3-5-haiku-20241022",
    name="anthropic_simple_agent",
    instructions="You are a helpful assistant using Claude. Provide clear, concise answers.",
    model_settings={
        "temperature": 0.3,
        "max_tokens": 200,
    },
)


anthropic_math_agent = Agent(
    "anthropic:claude-3-5-haiku-20241022",
    name="anthropic_math_agent",
    instructions="You are a mathematical assistant using Claude. Use the available tools to perform calculations and return structured results.",
    output_type=CalculationResult,
    model_settings={
        "temperature": 0.1,
        "max_tokens": 300,
    },
)


@anthropic_math_agent.tool_plain
def anthropic_add(a: int, b: int) -> int:
    """Add two numbers together (Anthropic version)."""
    return a + b


@anthropic_math_agent.tool_plain
def anthropic_multiply(a: int, b: int) -> int:
    """Multiply two numbers together (Anthropic version)."""
    return a * b


@anthropic_math_agent.tool_plain
def anthropic_calculate_percentage(part: float, total: float) -> float:
    """Calculate what percentage 'part' is of 'total' (Anthropic version)."""
    if total == 0:
        return 0.0
    return (part / total) * 100
