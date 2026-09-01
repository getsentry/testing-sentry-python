import asyncio
import os

from anthropic import AsyncAnthropic

import sentry_sdk
from sentry_sdk.consts import SPANTEMPLATE
from sentry_sdk.integrations.anthropic import AnthropicIntegration


@sentry_sdk.trace(name="Custom AI Agent", template=SPANTEMPLATE.AI_AGENT)
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
        trace_lifecycle="stream",
        send_default_pii=True,
        debug=True,
        integrations=[
            AnthropicIntegration(include_prompts=True),
        ],
    )

    client = AsyncAnthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    with sentry_sdk.start_transaction(name="anthropic-async"):
        await my_custom_agent(client)


asyncio.run(main())
