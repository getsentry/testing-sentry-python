from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions
import os

import sentry_sdk
from sentry_sdk.integrations.google_genai import GoogleGenAIIntegration

load_dotenv()

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    traces_sample_rate=1.0,
    integrations=[GoogleGenAIIntegration()],
    debug=True,
)


client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_VERTEX_PROJECT"],
    location=os.environ["GOOGLE_VERTEX_LOCATION"],
    http_options=HttpOptions(api_version="v1"),
)


def main():
    with sentry_sdk.start_transaction(op="test-transaction", name="test-chats"):
        chat = client.chats.create(model="gemini-2.0-flash")
        response = chat.send_message("What is the weather like in San Francisco, CA?")

    print(response.text)


if __name__ == "__main__":
    main()
