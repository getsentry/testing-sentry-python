import os
import uuid

from openai import OpenAI

import sentry_sdk
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.ai.utils import set_conversation_id
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration


@ai_track("Multi-turn conversation workflow")
def conversation_workflow(client):
    # Generate a unique conversation ID for this session
    conversation_id = str(uuid.uuid4())
    print(f"Conversation ID: {conversation_id}")

    # Set the conversation ID for all subsequent AI calls
    set_conversation_id(conversation_id)

    messages = []

    with sentry_sdk.start_transaction(name="openai-conversation"):
        # Turn 1: Initial question
        messages.append({"role": "user", "content": "Hi! I'm planning a trip to Japan. What's the best time to visit?"})

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=200,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("Turn 1 - User: Hi! I'm planning a trip to Japan. What's the best time to visit?")
        print(f"Turn 1 - Assistant: {assistant_message}")

        # Turn 2: Follow-up question
        messages.append({"role": "user", "content": "What about cherry blossom season? When does that happen?"})

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=200,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("Turn 2 - User: What about cherry blossom season? When does that happen?")
        print(f"Turn 2 - Assistant: {assistant_message}")

        # Turn 3: Another follow-up
        messages.append({"role": "user", "content": "Can you recommend some must-see places in Tokyo?"})

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=200,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("Turn 3 - User: Can you recommend some must-see places in Tokyo?")
        print(f"Turn 3 - Assistant: {assistant_message}")


@ai_track("Interleaved conversations workflow")
def interleaved_conversations_workflow(client):
    """Two conversations happening simultaneously, interleaved."""
    # Generate unique conversation IDs for both sessions
    conversation_id_a = str(uuid.uuid4())
    conversation_id_b = str(uuid.uuid4())
    print(f"Conversation A ID: {conversation_id_a}")
    print(f"Conversation B ID: {conversation_id_b}")

    messages_a = []
    messages_b = []

    with sentry_sdk.start_transaction(name="openai-interleaved-conversations"):
        # Conversation A - Turn 1
        set_conversation_id(conversation_id_a)
        messages_a.append({"role": "user", "content": "I want to learn Python. Where should I start?"})

        response = client.chat.completions.create(
            messages=messages_a,
            model="gpt-4o-mini",
            max_tokens=100,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages_a.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("[Conv A - Turn 1] User: I want to learn Python. Where should I start?")
        print(f"[Conv A - Turn 1] Assistant: {assistant_message}")

        # Conversation B - Turn 1
        set_conversation_id(conversation_id_b)
        messages_b.append({"role": "user", "content": "What's a good recipe for pasta?"})

        response = client.chat.completions.create(
            messages=messages_b,
            model="gpt-4o-mini",
            max_tokens=100,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages_b.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("[Conv B - Turn 1] User: What's a good recipe for pasta?")
        print(f"[Conv B - Turn 1] Assistant: {assistant_message}")

        # Conversation A - Turn 2
        set_conversation_id(conversation_id_a)
        messages_a.append({"role": "user", "content": "What about web development with Python?"})

        response = client.chat.completions.create(
            messages=messages_a,
            model="gpt-4o-mini",
            max_tokens=100,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages_a.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("[Conv A - Turn 2] User: What about web development with Python?")
        print(f"[Conv A - Turn 2] Assistant: {assistant_message}")

        # Conversation B - Turn 2
        set_conversation_id(conversation_id_b)
        messages_b.append({"role": "user", "content": "Can you make it vegetarian?"})

        response = client.chat.completions.create(
            messages=messages_b,
            model="gpt-4o-mini",
            max_tokens=100,
            temperature=0.7,
        )
        assistant_message = response.choices[0].message.content
        messages_b.append({"role": "assistant", "content": assistant_message})
        print("--------------------------------")
        print("[Conv B - Turn 2] User: Can you make it vegetarian?")
        print(f"[Conv B - Turn 2] Assistant: {assistant_message}")


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
        environment=os.getenv("ENV", "openai-test-conversation"),
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

    interleaved_conversations_workflow(client)

    print("--------------------------------")
    print("Done!")


if __name__ == "__main__":
    main()
