import os

from openai import OpenAI

import sentry_sdk
from sentry_sdk.consts import SPANTEMPLATE, SPANDATA
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration


@sentry_sdk.trace(name="Get Weather", template=SPANTEMPLATE.AI_TOOL)
def get_weather(lat: float, lng: float) -> str:
    """
    Get the weather for a given latitude and longitude.
    """
    return "sunny"


@sentry_sdk.trace(template=SPANTEMPLATE.AI_CHAT)
def chat(client, input: str):
    return "Bla"


@sentry_sdk.trace(name="My Agent", template=SPANTEMPLATE.AI_AGENT)
def my_socalled_agent(client):
    sentry_sdk.update_current_span(attributes={
        SPANDATA.GEN_AI_REQUEST_MODEL: "gpt-4o-mini",
        SPANDATA.GEN_AI_REQUEST_AVAILABLE_TOOLS: "[{'type': 'function', 'name': 'get_weather', 'description': 'Get current weather', 'parameters': {'type': 'object', 'properties': {'lat': {'type': 'number'}, 'lng': {'type': 'number'}}, 'required': ['lat', 'lng'], 'additionalProperties': False}, 'strict': True}]",
        SPANDATA.GEN_AI_REQUEST_MESSAGES: "What is the weather in Paris?",
        SPANDATA.GEN_AI_REQUEST_TEMPERATURE: 0.2,
        SPANDATA.GEN_AI_REQUEST_TOP_P: 0.7,
    })

    chat(client, "What is the weather in Paris?")
    get_weather(48.8566, 2.3522)
    chat(client, "What is the weather in Paris2?")

    sentry_sdk.update_current_span(attributes={
        SPANDATA.GEN_AI_RESPONSE_MODEL: "gpt-4o-mini-xxx",
        SPANDATA.GEN_AI_RESPONSE_TEXT: "Nice and sunny",
        SPANDATA.GEN_AI_USAGE_INPUT_TOKENS: 10,
        SPANDATA.GEN_AI_USAGE_OUTPUT_TOKENS: 10,
        SPANDATA.GEN_AI_USAGE_TOTAL_TOKENS: 20,
    })


def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "openai-test-sync"),
        traces_sample_rate=1.0,
        trace_lifecycle="stream",
        profiles_sample_rate=1.0,
        send_default_pii=True,
        debug=True,
        integrations=[
            OpenAIIntegration(include_prompts=True),
        ],
        disabled_integrations=[
            StdlibIntegration(),
        ],
    )

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    with sentry_sdk.start_transaction(name="main"):
        my_socalled_agent(client)

    print("--------------------------------")
    print("Done!")


if __name__ == "__main__":
    main()
