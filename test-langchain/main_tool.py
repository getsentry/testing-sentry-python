import os
import json
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.langchain import LangchainIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.anthropic import AnthropicIntegration


@tool
def get_weather(location: str) -> str:
    """Get the current weather in a given location."""
    return f"The weather in {location} is sunny with a high of 23°C."


@tool
def calculate_tip(bill_amount: float, tip_percentage: float) -> float:
    """Calculate tip amount based on bill and percentage."""
    return bill_amount * (tip_percentage / 100)


@tool
def mcp_database_query(query: str) -> Dict[str, Any]:
    """Execute a database query via MCP protocol. This tool may fail with various errors."""
    # Simulate MCP protocol communication
    mcp_request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "database/query",
        "params": {
            "query": query,
            "timeout": 5000
        }
    }

    # Log the request for debugging (in a real implementation, this would be sent over the network)
    print(f"MCP Request: {json.dumps(mcp_request, indent=2)}")

    # Simulate different types of MCP errors based on query content
    if "DROP" in query.upper():
        # Simulate MCP permission error
        error_response = {
            "jsonrpc": "2.0",
            "id": "1",
            "error": {
                "code": -32001,
                "message": "MCP Permission Denied",
                "data": {
                    "type": "permission_error",
                    "details": "DROP operations are not allowed via MCP"
                }
            }
        }
        raise Exception(f"MCP Error: {json.dumps(error_response, indent=2)}")

    elif "invalid" in query.lower():
        # Simulate MCP protocol error
        error_response = {
            "jsonrpc": "2.0",
            "id": "1",
            "error": {
                "code": -32602,
                "message": "Invalid SQL syntax",
                "data": {
                    "type": "syntax_error",
                    "position": 15,
                    "details": "Unexpected token 'invalid'"
                }
            }
        }
        raise ValueError(f"MCP SQL Error: {json.dumps(error_response, indent=2)}")

    elif "timeout" in query.lower():
        # Simulate MCP timeout error
        error_response = {
            "jsonrpc": "2.0",
            "id": "1",
            "error": {
                "code": -32000,
                "message": "MCP Request Timeout",
                "data": {
                    "type": "timeout_error",
                    "timeout_ms": 5000,
                    "details": "Database query exceeded maximum execution time"
                }
            }
        }
        raise TimeoutError(f"MCP Timeout: {json.dumps(error_response, indent=2)}")

    # Successful response for valid queries
    return {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "rows": [
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25}
            ],
            "affected_rows": 2,
            "execution_time_ms": 145
        }
    }


def create_agent_executor(llm, tools):
    """Create and return the agent executor."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can use tools to help answer questions."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


@sentry_sdk.trace(name="Individual LangChain tool test", attributes={"sentry.op": "ai.pipeline"})
def run_test_case(agent_executor, test_name, input_text, expect_error=False):
    """Run a single test case in its own transaction."""
    with sentry_sdk.start_span(name=f"langchain-tool-{test_name}"):
        print(f"\n{test_name}:")
        try:
            if "streaming" in test_name.lower():
                # Handle streaming case
                for chunk in agent_executor.stream({"input": input_text}):
                    print(chunk)
            else:
                # Handle regular invoke case
                result = agent_executor.invoke({"input": input_text})
                print(result)
        except Exception as e:
            if expect_error:
                print(f"Expected error: {e}")
            else:
                print(f"Unexpected error: {e}")
                raise


@sentry_sdk.trace(name="My sync LangChain tool AI pipeline", attributes={"sentry.op": "ai.pipeline"})
def my_pipeline(llm, tools, provider_name="unknown"):
    # Create agent executor once upfront
    agent_executor = create_agent_executor(llm, tools)

    # Define test cases
    test_cases = [
        {
            "name": f"{provider_name}-weather-tool",
            "input": "What's the weather like in San Francisco, CA?",
            "expect_error": False
        },
        {
            "name": f"{provider_name}-tip-calculation",
            "input": "Calculate a 18% tip on a $45.50 bill",
            "expect_error": False
        },
        {
            "name": f"{provider_name}-streaming-multiple-tools",
            "input": "What's the weather in New York and calculate a 20% tip on $30?",
            "expect_error": False
        },
        {
            "name": f"{provider_name}-mcp-successful-query",
            "input": "Execute this database query: SELECT * FROM users LIMIT 2",
            "expect_error": False
        },
        {
            "name": f"{provider_name}-mcp-permission-error",
            "input": "Execute this database query: DROP TABLE users",
            "expect_error": True
        },
        {
            "name": f"{provider_name}-mcp-syntax-error",
            "input": "Execute this database query: SELECT invalid syntax FROM nowhere",
            "expect_error": True
        },
        {
            "name": f"{provider_name}-mcp-timeout-error",
            "input": "Execute this slow database query that will timeout: SELECT * FROM large_table",
            "expect_error": True
        }
    ]

    # Run each test case in its own transaction
    for test_case in test_cases:
        run_test_case(
            agent_executor,
            test_case["name"],
            test_case["input"],
            test_case["expect_error"]
        )


def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        debug=True,
        integrations=[
            LangchainIntegration(),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        disabled_integrations=[OpenAIIntegration(), AnthropicIntegration()],
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    tools = [get_weather, calculate_tip, mcp_database_query]

    # Test with OpenAI
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        print("=== Testing with OpenAI ===")
        openai_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
            temperature=0,
        )
        my_pipeline(openai_llm, tools, "openai")
    else:
        print("Skipping OpenAI tests - no API key found")

    # Test with Anthropic
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        print("\n=== Testing with Anthropic ===")
        anthropic_llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            api_key=anthropic_api_key,
            temperature=0,
        )
        my_pipeline(anthropic_llm, tools, "anthropic")
    else:
        print("Skipping Anthropic tests - no API key found")

    if not openai_api_key and not anthropic_api_key:
        print("No API keys found. Please set OPENAI_API_KEY and/or ANTHROPIC_API_KEY environment variables.")


if __name__ == "__main__":
    main()
