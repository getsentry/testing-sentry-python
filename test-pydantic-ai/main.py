"""
Synchronous Pydantic AI tests with Sentry integration.
Tests: simple agent, agent with tools, two-agent workflow.
Includes both streaming and non-streaming tests.
"""

import os
import sentry_sdk
from sentry_sdk.integrations.pydantic_ai import PydanticAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration

from agents import (
    simple_agent,
    math_agent,
    data_collector_agent,
    data_analyzer_agent,
    anthropic_simple_agent,
    anthropic_math_agent,
)


def test_simple_agent():
    """Test simple agent without tools."""
    print("\n=== SIMPLE AGENT ===")
    
    result = simple_agent.run_sync("What is the capital of France? Keep it brief.")
    print(f"Question: What is the capital of France?")
    print(f"Answer: {result.output}")




def test_agent_with_tools():
    """Test agent with mathematical tools."""
    print("\n=== AGENT WITH TOOLS ===")
    
    result = math_agent.run_sync(
        "Calculate 15 + 27, then multiply the result by 3. "
        "Also calculate what percentage 42 is of 100. "
        "Explain your work step by step."
    )
    print(f"Task: Multi-step calculation")
    print(f"Result: {result.output}")




def test_two_agent_workflow():
    """Test two-agent workflow."""
    print("\n=== TWO-AGENT WORKFLOW ===")
    
    # Step 1: Data Collector
    print("Step 1: Data Collection")
    raw_data = "Sales report: January 150 units, February 200 units, March 175 units, April 225 units"
    
    collection_result = data_collector_agent.run_sync(
        f"Extract and organize the numerical data from this text: {raw_data}"
    )
    print(f"Data Collector Result: {collection_result.output}")
    
    # Step 2: Data Analyzer (using the collected data)
    print("\nStep 2: Data Analysis")
    analysis_result = data_analyzer_agent.run_sync(
        f"Analyze this sales data and provide insights: {collection_result.output}. "
        "The data represents monthly sales units. Identify trends and make recommendations."
    )
    print(f"Data Analyzer Result: {analysis_result.output}")


def test_anthropic_simple_agent():
    """Test Anthropic simple agent without tools."""
    print("\n=== ANTHROPIC SIMPLE AGENT ===")
    
    result = anthropic_simple_agent.run_sync("What is the capital of Italy? Keep it brief.")
    print(f"Question: What is the capital of Italy?")
    print(f"Answer: {result.output}")


def test_anthropic_agent_with_tools():
    """Test Anthropic agent with mathematical tools."""
    print("\n=== ANTHROPIC AGENT WITH TOOLS ===")
    
    result = anthropic_math_agent.run_sync(
        "Calculate 12 + 18, then multiply the result by 4. "
        "Also calculate what percentage 25 is of 80. "
        "Show your work step by step."
    )
    print(f"Task: Multi-step calculation with Claude")
    print(f"Result: {result.output}")


def main():
    """Run all synchronous tests."""
    # Initialize Sentry
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENV", "test-sync"),
        traces_sample_rate=1.0,
        send_default_pii=True,
        integrations=[PydanticAIIntegration()],
        disabled_integrations=[StdlibIntegration()],
        debug=True,
    )

    # Set user context
    sentry_sdk.set_user({"id": "test-user", "email": "test@example.com"})
    sentry_sdk.set_tag("test_type", "pydantic_ai_sync")

    print("🚀 Running Pydantic AI Synchronous Tests")
    print("=" * 50)

    # Run all tests
    test_simple_agent()
    test_agent_with_tools()
    test_two_agent_workflow()
    
    # Run Anthropic provider tests
    test_anthropic_simple_agent()
    test_anthropic_agent_with_tools()

    print("\n" + "=" * 50)
    print("✅ All synchronous tests completed!")


if __name__ == "__main__":
    main()