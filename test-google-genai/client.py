from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.types import HttpOptions
import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.google_genai import GoogleGenAIIntegration

load_dotenv()

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    traces_sample_rate=1.0,
    integrations=[GoogleGenAIIntegration(), LoggingIntegration(event_level=logging.ERROR, level=None)],
    debug=True,
    data_collection={"stack_frame_variables": {"mode": "denylist"}},
    attach_stacktrace=False,
)

client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_VERTEX_PROJECT"],
    location=os.environ["GOOGLE_VERTEX_LOCATION"],
    http_options=HttpOptions(api_version="v1"),
)


def get_current_weather(location: str) -> str:
    """Returns the current weather.

    Args:
      location: The city and state, e.g. San Francisco, CA
    """
    return "sunny"


google_search_retrieval_tool = {"google_search": {}}


def main():
    with sentry_sdk.start_span(name="test", attributes={"sentry.op": "test-transaction"}):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is weather like in Boston, MA?",
            config=types.GenerateContentConfig(
                tools=[get_current_weather],
                system_instruction="You are a helpful assistant that can use tools to help answer questions.",
                temperature=0.2,
            ),
        )

    print(response.text)


if __name__ == "__main__":
    main()
