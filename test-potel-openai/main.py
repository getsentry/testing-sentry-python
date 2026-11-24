import os
import time
from openai import OpenAI

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import logger as sentry_logger
from sentry_sdk.consts import VERSION as SENTRY_SDK_VERSION
from sentry_sdk.feature_flags import add_feature_flag
from sentry_sdk.integrations.openai import OpenAIIntegration

DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__)))


def _fibonacci(n):
    print(f"fibonacci {n}")
    time.sleep(0.05)

    if n < 0:
        raise ValueError("Incorrect input: n must be non-negative")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return _fibonacci(n-1) + _fibonacci(n-2)


@sentry_sdk.trace(name="My sync OpenAI pipeline", attributes={"sentry.op": "ai.pipeline"})
def my_pipeline(client):
    user = {
        "id": "testuser",
        "username": "Test User",
    }

    # feature flag
    add_feature_flag("test-flag", True)

    # spans

    with sentry_sdk.start_span(name="test-span-2"):

        # tag
        sentry_sdk.set_tag("test-tag", "test-value")

        # user
        sentry_sdk.set_user(user)

        # breadcrumb
        sentry_sdk.add_breadcrumb(
            category="test-category",
            message="test breadcrumb",
            level="info",
            data={"user": user},
        )

        # context
        sentry_sdk.set_context("test-context", {"text-context-user": user})

        # attachments
        sentry_sdk.add_attachment(bytes=b"Hello Error World", filename="hello-on-error.txt")
        sentry_sdk.add_attachment(bytes=b"Hello Transaction World", filename="hello-on-transaction.txt")

        # logs
        sentry_logger.warning("test log")

        # do some work, so we have a profile
        _fibonacci(5)

        # Sync create message
        message = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hi!",
                }
            ],
            model="gpt-3.5-turbo",
        )
        print("Message:")
        print(message.dict())

        # Sync embeddings
        embedding = client.embeddings.create(
            input="Your text goes here",
            model="text-embedding-3-small",
        ).data[0].embedding
        print("Embedding:")
        print(len(embedding))

        # Sentry does not instrument streaming OpenAI API calls
        # # Sync create streaming message
        # stream = client.chat.completions.create(
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": "Hi!",
        #         }
        #     ],
        #     model="gpt-3.5-turbo",
        #     stream=True,
        # )
        # print("Message (Stream):")
        # for event in stream:
        #     print(event)

        # raise an error
        raise ValueError("help! an error!")


def main():
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=f"{DIR}-{SENTRY_SDK_VERSION}-sync",
        release=SENTRY_SDK_VERSION,
        integrations=[
            OpenAIIntegration(),
            LoggingIntegration(event_level=logging.ERROR),
        ],
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        debug=True,
        spotlight="http://localhost:9999/api/0/envelope/",
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    with sentry_sdk.start_span(name="test-span-openai-sync"):
        my_pipeline(client)


if __name__ == "__main__":
    main()
