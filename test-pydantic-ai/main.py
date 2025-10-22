"""
Comprehensive Pydantic AI tests with Sentry integration.
Tests all combinations of agents, models, and execution methods.

Test matrix: 3 agent types × 2 models × 5 methods = 30 tests
"""

import os
import asyncio
import sentry_sdk
from sentry_sdk.integrations.pydantic_ai import PydanticAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration

from agents import (
    create_customer_support_agent,
    create_math_agent,
    create_mcp_agent,
    CustomerContext,
)


# Test data
GOLD_CUSTOMER = CustomerContext(
    customer_id="CUST001",
    name="Alice Johnson",
    tier="gold",
    account_balance=1500.0,
    open_tickets=1,
    last_purchase_days_ago=5
)


# Models to test
MODELS = [
    "openai:gpt-4o-mini",
    "anthropic:claude-3-5-haiku-20241022",
]


def test_run_sync(agent_factory, model: str, agent_type: str):
    """Test synchronous execution."""
    agent = agent_factory(f"{model.split(':')[0]}_{agent_type}_run_sync", model)
    
    if agent_type == "customer_support":
        agent.run_sync(
            "I'm interested in priority support and a 10% discount. Am I eligible?",
            deps=GOLD_CUSTOMER
        )
    elif agent_type == "math_agent":
        agent.run_sync(
            "Calculate 25 + 17, then multiply the result by 3. "
            "Also calculate what percentage 42 is of 100."
        )
    else:  # mcp_agent
        agent.run_sync("Add 15 and 27, then multiply the result by 2.")


async def test_run(agent_factory, model: str, agent_type: str):
    """Test async execution."""
    agent = agent_factory(f"{model.split(':')[0]}_{agent_type}_run", model)
    
    if agent_type == "customer_support":
        await agent.run(
            "Can I get free shipping on my next order?",
            deps=GOLD_CUSTOMER
        )
    elif agent_type == "math_agent":
        await agent.run(
            "Calculate (15 + 25) * 2, then divide the result by 4."
        )
    else:  # mcp_agent
        async with agent:
            await agent.run("Multiply 12 by 8, then add 5.")


async def test_run_stream(agent_factory, model: str, agent_type: str):
    """Test streaming execution."""
    agent = agent_factory(f"{model.split(':')[0]}_{agent_type}_run_stream", model)
    
    if agent_type == "customer_support":
        async with agent.run_stream(
            "What perks am I eligible for as a gold member?",
            deps=GOLD_CUSTOMER
        ) as result:
            # Structured outputs can't use stream_text(), just wait for completion
            pass
    elif agent_type == "math_agent":
        async with agent.run_stream(
            "Calculate 100 - 25, multiply by 3, and calculate the percentage of 500."
        ) as result:
            # Structured outputs can't use stream_text(), just wait for completion
            pass
    else:  # mcp_agent
        async with agent:
            async with agent.run_stream("Add 20 and 30.") as result:
                pass


async def test_iter(agent_factory, model: str, agent_type: str):
    """Test structured streaming with iter."""
    agent = agent_factory(f"{model.split(':')[0]}_{agent_type}_iter", model)
    
    if agent_type == "customer_support":
        async with agent.iter(
            "Check my eligibility for early access and priority support perks.",
            deps=GOLD_CUSTOMER
        ) as result:
            async for _ in result:
                pass
    elif agent_type == "math_agent":
        async with agent.iter(
            "Calculate 10 + 20 + 30, then multiply by 2."
        ) as result:
            async for _ in result:
                pass
    else:  # mcp_agent
        async with agent:
            async with agent.iter("Multiply 5 by 6.") as result:
                async for _ in result:
                    pass


async def test_run_stream_events(agent_factory, model: str, agent_type: str):
    """Test event streaming with run_stream_events."""
    agent = agent_factory(f"{model.split(':')[0]}_{agent_type}_run_stream_events", model)
    
    if agent_type == "customer_support":
        async for _ in agent.run_stream_events(
            "What perks am I eligible for with my tier?",
            deps=GOLD_CUSTOMER
        ):
            pass
    elif agent_type == "math_agent":
        async for _ in agent.run_stream_events(
            "Calculate 50 + 30, then multiply by 2."
        ):
            pass
    else:  # mcp_agent
        async with agent:
            async for _ in agent.run_stream_events("Add 7 and 8."):
                pass


async def run_all_async_tests():
    """Run all async tests for all combinations."""
    agent_factories = [
        (create_customer_support_agent, "customer_support"),
        (create_math_agent, "math_agent"),
        (create_mcp_agent, "mcp_agent"),
    ]
    
    for model in MODELS:
        for agent_factory, agent_type in agent_factories:
            await test_run(agent_factory, model, agent_type)
            await test_run_stream(agent_factory, model, agent_type)
            await test_iter(agent_factory, model, agent_type)
            await test_run_stream_events(agent_factory, model, agent_type)


def main():
    """Run all tests."""
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENV", "test-pydantic-ai"),
        traces_sample_rate=1.0,
        send_default_pii=True,
        integrations=[PydanticAIIntegration()],
        disabled_integrations=[StdlibIntegration(), OpenAIIntegration()],
        debug=True,
    )

    sentry_sdk.set_user({"id": "test-user", "email": "test@example.com"})
    sentry_sdk.set_tag("test_type", "pydantic_ai_comprehensive")

    print("🚀 Running Pydantic AI Tests")

    agent_factories = [
        (create_customer_support_agent, "customer_support"),
        (create_math_agent, "math_agent"),
        (create_mcp_agent, "mcp_agent"),
    ]

    # Run synchronous tests
    for model in MODELS:
        for agent_factory, agent_type in agent_factories:
            test_run_sync(agent_factory, model, agent_type)

    # Run async tests
    asyncio.run(run_all_async_tests())


if __name__ == "__main__":
    main()
