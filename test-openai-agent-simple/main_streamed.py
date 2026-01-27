import asyncio
import os

from agents import Agent, Runner, function_tool
from pydantic import BaseModel
from simpleeval import simple_eval

import sentry_sdk
from sentry_sdk.integrations.openai_agents import OpenAIAgentsIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration


@function_tool
def calculate(expression: str):
    """
    A tool for evaluating mathematical expressions.
    Example expressions:
        '1.2 * (2 + 4.5)', '12.7 cm to inch'
        'sin(45 deg) ^ 2'
    """
    # Remove any whitespace
    expression = expression.strip()

    # Evaluate the expression
    result = simple_eval(expression)

    # If the result is a float, round it to 6 decimal places
    if isinstance(result, float):
        result = round(result, 6)

    return result


class FinalResult(BaseModel):
    number: float


INSTRUCTIONS = (
    "You are solving math problems. "
    "Reason step by step. "
    "Use the calculator when necessary. "
    "When you give the final answer, "
    "provide an explanation for how you arrived at it. "
)


math_agent = Agent(
    name="MathAgent",
    instructions=INSTRUCTIONS,
    tools=[calculate],
    model="gpt-4o",
    output_type=FinalResult,
)


PROMPT = (
    "A taxi driver earns $9461 per 1-hour of work. "
    "If he works 12 hours a day and in 1 hour "
    "he uses 12 liters of petrol with a price of $134 for 1 liter. "
    "How much money does he earn in one day?"
)


def before_send_transaction(event, hint):
    """Print gen_ai attributes from all spans before sending transaction."""
    print("\n" + "=" * 80)
    print("TRANSACTION EVENT - Printing all spans with gen_ai attributes")
    print("=" * 80)

    spans = event.get("spans", [])
    for span in spans:
        op = span.get("op", "unknown")
        description = span.get("description", "no description")
        span_id = span.get("span_id", "unknown")
        data = span.get("data", {})

        # Filter gen_ai prefixed attributes
        gen_ai_attrs = {k: v for k, v in data.items() if k.startswith("gen_ai")}

        if gen_ai_attrs:
            print(f"\nSPAN: {op} - {description}")
            print(f"Span ID: {span_id}")
            print("gen_ai attributes:")
            for key, value in sorted(gen_ai_attrs.items()):
                print(f"  {key}: {value}")

    print("=" * 80 + "\n")
    return event


async def main() -> None:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENV", "test"),
        traces_sample_rate=1.0,
        send_default_pii=True,
        # before_send_transaction=before_send_transaction,
        integrations=[OpenAIAgentsIntegration()],
        disabled_integrations=[
            StdlibIntegration(),
        ],
        debug=True,
    )

    print("Starting streamed run...")
    print(f"Input: {PROMPT}")

    result = Runner.run_streamed(math_agent, input=PROMPT)

    async for event in result.stream_events():
        # Ignore raw response event deltas for cleaner output
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                # Access tool name from raw_item if available
                tool_name = getattr(event.item.raw_item, "name", "unknown")
                print(f"-- Tool called: {tool_name}")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output: {event.item}")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
