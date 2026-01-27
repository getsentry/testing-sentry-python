import os

from openai import OpenAI

import sentry_sdk
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration


@ai_track("Streamed OpenAI workflow")
def streamed_workflow(client):
    with sentry_sdk.start_transaction(name="openai-streamed"):
        # Chat Completions API with streaming
        print("Starting streamed chat completion...")
        stream = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that explains things concisely.",
                },
                {
                    "role": "user",
                    "content": "Explain how photosynthesis works in 3 sentences.",
                }
            ],
            model="gpt-4o-mini",
            max_tokens=200,
            temperature=0.7,
            stream=True,
        )

        print("--------------------------------")
        print("Streamed Response:")
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)
        print("\n--------------------------------")
        print(f"Full response length: {len(full_response)} chars")

        # Responses API with streaming
        print("\nStarting streamed responses API...")
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a helpful assistant.",
            input="What are the three primary colors?",
            temperature=0.5,
            stream=True,
        )
        print("--------------------------------")
        print("Streamed Responses API:")
        for chunk in response:
            print(f"Chunk type: {chunk.type}")
            if hasattr(chunk, 'delta') and chunk.delta:
                print(f"  Delta: {chunk.delta}")
        print("--------------------------------")


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


def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "openai-test-streamed"),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        send_default_pii=True,
        debug=True,
        before_send_transaction=before_send_transaction,
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

    streamed_workflow(client)

    print("--------------------------------")
    print("Done!")


if __name__ == "__main__":
    main()
