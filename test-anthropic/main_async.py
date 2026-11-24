import asyncio
import os

from anthropic import AsyncAnthropic

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.traces
from sentry_sdk.integrations.anthropic import AnthropicIntegration


@sentry_sdk.trace(name="Custom AI Agent", attributes={"sentry.op": "gen_ai.invoke_agent"})
async def my_custom_agent(client):
    print("~~~ Starting my_custom_agent ~~~")

    # Async create message
    message = await client.messages.create(
        messages=[
            {
                "role": "user",
                "content": "Hi!",
            }
        ],
        model="claude-3-haiku-20240307",
        max_tokens=1024,
    )
    print("~~~ First result (async message): ~~~")
    print(message.model_dump())

    # Async create streaming message
    stream = await client.messages.create(
        messages=[
            {
                "role": "user",
                "content": "Hi!",
            }
        ],
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        stream=True,
    )
    print("~~~ Second result (async streaming message): ~~~")
    async for event in stream:
        print(event.model_dump())

    print("~~~ Done ~~~")


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        debug=True,
        integrations=[
            AnthropicIntegration(),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    client = AsyncAnthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    with sentry_sdk.traces.start_span(name="anthropic-async"):
        await my_custom_agent(client)


asyncio.run(main())
