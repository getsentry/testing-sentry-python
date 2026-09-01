import os

from openai import OpenAI

import sentry_sdk
import sentry_sdk.traces
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}, {
    "type": "web_search_preview",
    "user_location": {
        "type": "approximate",
        "country": "GB",
        "city": "London",
        "region": "London"
    }
}]

@ai_track("My sync OpenAI workflow")
def my_workflow(client):
    with sentry_sdk.traces.start_span(name="openai-sync"):
        # Responses API with tools
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a assistant that talks like a pirate.",
            input="What is the weather in Paris?",
            tools=tools,
            temperature=0.2,
            top_p=0.3,
        )
        print("--------------------------------")
        print("Response:")
        print(response.model_dump())

        # Responses API with streaming
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a assistant that talks like a pirate.",
            input="What is the weather in Paris?",
            temperature=0.2,
            top_p=0.3,
            stream=True,
        )
        print("--------------------------------")
        print("Streaming Response:")
        for chunk in response:
            print("Chunk:")
            print(chunk.model_dump())

        # Completions API
        message = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hi!",
                }
            ],
            model="gpt-3.5-turbo",
            max_tokens=666,
            presence_penalty=0.1,
            temperature=0.2,
            top_p=0.3,
        )
        print("--------------------------------")
        print("Message:")
        print(message.model_dump())

        # Embeddings API
        embeddings = client.embeddings.create(
            input="The text I want to calculate the embeddings for. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            model="text-embedding-3-small",
        ).data[0].embedding
        print("--------------------------------")
        print("Embeddings:")
        print(len(embeddings))


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
            OpenAIIntegration(
                include_prompts=True,
                tiktoken_encoding_name="cl100k_base",
            ),
        ],
        disabled_integrations=[
            StdlibIntegration(),
        ],
    )

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    my_workflow(client)

    print("--------------------------------")
    print("Done!")


if __name__ == "__main__":
    main()
