import asyncio
import os
import uuid

from openai import AsyncOpenAI

import sentry_sdk
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.ai.utils import set_conversation_id
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration


async def conversation_a(client, conversation_id: str):
    """First conversation about learning Python."""
    set_conversation_id(conversation_id)
    messages = []

    # Turn 1
    messages.append({"role": "user", "content": "I want to learn Python. Where should I start?"})
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7,
    )
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    print("--------------------------------")
    print("[Conv A - Turn 1] User: I want to learn Python. Where should I start?")
    print(f"[Conv A - Turn 1] Assistant: {assistant_message}")

    # Turn 2
    set_conversation_id(conversation_id)  # Re-set after potential context switch
    messages.append({"role": "user", "content": "What about web development with Python?"})
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7,
    )
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    print("--------------------------------")
    print("[Conv A - Turn 2] User: What about web development with Python?")
    print(f"[Conv A - Turn 2] Assistant: {assistant_message}")

    return "Conversation A complete"


async def conversation_b(client, conversation_id: str):
    """Second conversation about cooking."""
    set_conversation_id(conversation_id)
    messages = []

    # Turn 1
    messages.append({"role": "user", "content": "What's a good recipe for pasta?"})
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7,
    )
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    print("--------------------------------")
    print("[Conv B - Turn 1] User: What's a good recipe for pasta?")
    print(f"[Conv B - Turn 1] Assistant: {assistant_message}")

    # Turn 2
    set_conversation_id(conversation_id)  # Re-set after potential context switch
    messages.append({"role": "user", "content": "Can you make it vegetarian?"})
    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        max_tokens=100,
        temperature=0.7,
    )
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    print("--------------------------------")
    print("[Conv B - Turn 2] User: Can you make it vegetarian?")
    print(f"[Conv B - Turn 2] Assistant: {assistant_message}")

    return "Conversation B complete"


@ai_track("Concurrent conversations workflow")
async def concurrent_conversations_workflow(client):
    """Two conversations running concurrently with asyncio.gather()."""
    # Generate unique conversation IDs for both sessions
    conversation_id_a = str(uuid.uuid4())
    conversation_id_b = str(uuid.uuid4())
    print(f"Conversation A ID: {conversation_id_a}")
    print(f"Conversation B ID: {conversation_id_b}")

    with sentry_sdk.start_transaction(name="openai-concurrent-conversations"):
        # Run both conversations concurrently
        results = await asyncio.gather(
            conversation_a(client, conversation_id_a),
            conversation_b(client, conversation_id_b),
        )
        print("--------------------------------")
        print(f"Results: {results}")


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


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "openai-test-conversation-async"),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        send_default_pii=True,
        debug=True,
        before_send_transaction=before_send_transaction,
        integrations=[
            AsyncioIntegration(),
            OpenAIIntegration(
                include_prompts=True,
                tiktoken_encoding_name="cl100k_base",
            ),
        ],
        disabled_integrations=[
            StdlibIntegration(),
        ],
    )

    client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    await concurrent_conversations_workflow(client)

    print("--------------------------------")
    print("Done!")


asyncio.run(main())
