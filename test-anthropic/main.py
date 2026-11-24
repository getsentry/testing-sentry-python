import os

from anthropic import Anthropic

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.anthropic import AnthropicIntegration


@sentry_sdk.trace(name="Custom AI Agent", attributes={"sentry.op": "gen_ai.invoke_agent"})
def my_custom_agent(client):
    print("~~~ Starting my_custom_agent ~~~")

    # Sync create message
    message = client.messages.create(
        messages=[
            {
                "role": "user",
                "content": "Hi!",
            }
        ],
        model="claude-3-5-haiku-latest",
        max_tokens=1024,
    )
    print("~~~ First result (sync message): ~~~")
    print(message.model_dump())

    # Sync create streaming message
    stream = client.messages.create(
        messages=[
            {
                "role": "user",
                "content": "Hi!",
            }
        ],
        model="claude-3-5-haiku-latest",
        max_tokens=1024,
        stream=True,
    )
    print("~~~ Second result (sync streaming message): ~~~")
    for event in stream:
        print(event.model_dump())

    print("~~~ Done ~~~")


def main():
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

    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    # with sentry_sdk.start_transaction(name="anthropic-sync"):
    my_custom_agent(client)


if __name__ == "__main__":
    main()
