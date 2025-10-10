"""
Asynchronous Pydantic AI tests with Sentry integration.
Tests: simple agent, agent with tools, two-agent workflow.
Includes both streaming and non-streaming tests.
"""

import asyncio
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


async def test_simple_agent():
    """Test simple agent without tools - non-streaming."""
    print("\n=== SIMPLE AGENT (Non-Streaming) ===")
    
    result = await simple_agent.run("What is the capital of Germany? Keep it brief.")
    print(f"Question: What is the capital of Germany?")
    print(f"Answer: {result.output}")


async def test_simple_agent_streaming():
    """Test simple agent without tools - streaming."""
    print("\n=== SIMPLE AGENT (Streaming) ===")
    
    print("Question: Explain photosynthesis in simple terms.")
    print("Answer (streaming): ", end="", flush=True)
    
    async with simple_agent.run_stream("Explain photosynthesis in simple terms, 2-3 sentences.") as result:
        async for chunk in result.stream_output():
            if hasattr(chunk, 'output') and chunk.output:
                print(chunk.output, end="", flush=True)
    print()  # New line after streaming


async def test_agent_with_tools():
    """Test agent with mathematical tools - non-streaming."""
    print("\n=== AGENT WITH TOOLS (Non-Streaming) ===")
    
    result = await math_agent.run(
        "Calculate 23 + 17, then multiply the result by 2. "
        "Also calculate what percentage 30 is of 120. "
        "Show your work clearly."
    )
    print(f"Task: Multi-step calculation")
    print(f"Result: {result.output}")


async def test_agent_with_tools_streaming():
    """Test agent with tools - streaming."""
    print("\n=== AGENT WITH TOOLS (Streaming) ===")
    
    print("Task: Calculate 18 * 6 and show the process")
    print("Result (streaming): ", end="", flush=True)
    
    async with math_agent.run_stream("Calculate 18 multiplied by 6 and show your calculation steps.") as result:
        async for chunk in result.stream_output():
            if hasattr(chunk, 'output') and chunk.output:
                print(chunk.output, end="", flush=True)
    print()  # New line after streaming


async def test_two_agent_workflow():
    """Test two-agent workflow - non-streaming."""
    print("\n=== TWO-AGENT WORKFLOW (Non-Streaming) ===")
    
    # Step 1: Data Collector
    print("Step 1: Data Collection")
    raw_data = "Quarterly revenue: Q1 $450K, Q2 $520K, Q3 $480K, Q4 $610K"
    
    collection_result = await data_collector_agent.run(
        f"Extract and organize the financial data from this text: {raw_data}"
    )
    print(f"Data Collector Result: {collection_result.output}")
    
    # Step 2: Data Analyzer (using the collected data)
    print("\nStep 2: Data Analysis")
    analysis_result = await data_analyzer_agent.run(
        f"Analyze this quarterly revenue data: {collection_result.output}. "
        "Identify trends and provide business recommendations."
    )
    print(f"Data Analyzer Result: {analysis_result.output}")


async def test_two_agent_workflow_streaming():
    """Test two-agent workflow - streaming."""
    print("\n=== TWO-AGENT WORKFLOW (Streaming) ===")
    
    # Step 1: Data Collector (streaming)
    print("Step 1: Data Collection (streaming)")
    raw_data = "Website traffic: Monday 1200 visits, Tuesday 1350 visits, Wednesday 980 visits, Thursday 1450 visits"
    
    print("Data Collector (streaming): ", end="", flush=True)
    collection_output = ""
    
    async with data_collector_agent.run_stream(
        f"Extract and organize this website traffic data: {raw_data}"
    ) as collection_result:
        async for chunk in collection_result.stream_output():
            if hasattr(chunk, 'output') and chunk.output:
                print(chunk.output, end="", flush=True)
                collection_output += chunk.output
    print()  # New line
    
    # Step 2: Data Analyzer (streaming)
    print("\nStep 2: Data Analysis (streaming)")
    print("Data Analyzer (streaming): ", end="", flush=True)
    
    async with data_analyzer_agent.run_stream(
        f"Analyze this website traffic data: {collection_output}. "
        "Calculate daily patterns and suggest optimization strategies."
    ) as analysis_result:
        async for chunk in analysis_result.stream_output():
            if hasattr(chunk, 'output') and chunk.output:
                print(chunk.output, end="", flush=True)
    print()  # New line


async def test_parallel_agents():
    """Test running multiple agents in parallel."""
    print("\n=== PARALLEL AGENTS ===")
    
    print("Running multiple agents in parallel...")
    
    # Run multiple agents concurrently
    tasks = [
        simple_agent.run("What is 2+2?"),
        math_agent.run("Calculate 5 * 8 and explain the result."),
        data_collector_agent.run("Extract numbers from: 'We sold 100 apples, 50 oranges, and 75 bananas.'"),
    ]
    
    results = await asyncio.gather(*tasks)
    
    print("Parallel Results:")
    print(f"1. Simple Agent: {results[0].output}")
    print(f"2. Math Agent: {results[1].output}")
    print(f"3. Data Collector: {results[2].output}")


async def test_anthropic_simple_agent():
    """Test Anthropic simple agent without tools - non-streaming."""
    print("\n=== ANTHROPIC SIMPLE AGENT (Non-Streaming) ===")
    
    result = await anthropic_simple_agent.run("What is the capital of Spain? Keep it brief.")
    print(f"Question: What is the capital of Spain?")
    print(f"Answer: {result.output}")


async def test_anthropic_simple_agent_streaming():
    """Test Anthropic simple agent without tools - streaming."""
    print("\n=== ANTHROPIC SIMPLE AGENT (Streaming) ===")
    
    print("Question: Explain gravity in simple terms.")
    print("Answer (streaming): ", end="", flush=True)
    
    async with anthropic_simple_agent.run_stream("Explain gravity in simple terms, 2-3 sentences.") as result:
        async for chunk in result.stream_output():
            if hasattr(chunk, 'output') and chunk.output:
                print(chunk.output, end="", flush=True)
    print()  # New line after streaming


async def test_anthropic_agent_with_tools():
    """Test Anthropic agent with mathematical tools - non-streaming."""
    print("\n=== ANTHROPIC AGENT WITH TOOLS (Non-Streaming) ===")
    
    result = await anthropic_math_agent.run(
        "Calculate 19 + 31, then multiply the result by 2. "
        "Also calculate what percentage 15 is of 60. "
        "Show your work clearly using Claude."
    )
    print(f"Task: Multi-step calculation with Claude")
    print(f"Result: {result.output}")


async def test_anthropic_agent_with_tools_streaming():
    """Test Anthropic agent with tools - streaming."""
    print("\n=== ANTHROPIC AGENT WITH TOOLS (Streaming) ===")
    
    print("Task: Calculate 14 * 9 with Claude and show the process")
    print("Result (streaming): ", end="", flush=True)
    
    async with anthropic_math_agent.run_stream("Calculate 14 multiplied by 9 and show your calculation steps using Claude.") as result:
        async for chunk in result.stream_output():
            if hasattr(chunk, 'output') and chunk.output:
                print(chunk.output, end="", flush=True)
    print()  # New line after streaming


async def main():
    """Run all asynchronous tests."""
    # Initialize Sentry
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENV", "test-async"),
        traces_sample_rate=1.0,
        send_default_pii=True,
        integrations=[PydanticAIIntegration()],
        disabled_integrations=[StdlibIntegration()],
        debug=True,
    )

    # Set user context
    sentry_sdk.set_user({"id": "test-user-async", "email": "test-async@example.com"})
    sentry_sdk.set_tag("test_type", "pydantic_ai_async")

    print("🚀 Running Pydantic AI Asynchronous Tests")
    print("=" * 50)

    # Run all tests
    await test_simple_agent()
    await test_simple_agent_streaming()
    await test_agent_with_tools()
    await test_agent_with_tools_streaming()
    await test_two_agent_workflow()
    await test_two_agent_workflow_streaming()
    await test_parallel_agents()
    
    # Run Anthropic provider tests
    await test_anthropic_simple_agent()
    await test_anthropic_simple_agent_streaming()
    await test_anthropic_agent_with_tools()
    await test_anthropic_agent_with_tools_streaming()

    print("\n" + "=" * 50)
    print("✅ All asynchronous tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
