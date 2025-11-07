import os

from openai import OpenAI

import sentry_sdk
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.integrations.openai import OpenAIIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
import dotenv

dotenv.load_dotenv()


def generate_long_message(index):
    base_message = f"Message number {index}: "
    filler = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. "
    
    message = base_message
    while len(message) < 1000:
        message += filler
    
    return message[:1000]


@ai_track("My truncation test workflow")
def my_truncation_workflow(client):
    with sentry_sdk.start_transaction(name="openai-truncation-test"):
        messages = []
        
        for i in range(25):
            if i % 2 == 0:
                messages.append({
                    "role": "user",
                    "content": generate_long_message(i)
                })
            else:
                messages.append({
                    "role": "assistant",
                    "content": generate_long_message(i)
                })
        
        messages.append({
            "role": "user",
            "content": "Please summarize our conversation so far in one sentence."
        })
        
        print(f"Total messages: {len(messages)}")
        total_chars = sum(len(msg["content"]) for msg in messages)
        print(f"Total characters in messages: {total_chars}")
        print(f"Approximate size in KB: {total_chars / 1024:.2f}")
        
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            max_tokens=100,
            temperature=0.7,
        )
        
        print("--------------------------------")
        print("Response:")
        print(response.model_dump())
        print("--------------------------------")
        print("Assistant reply:")
        print(response.choices[0].message.content)


def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "openai-test-truncation"),
        traces_sample_rate=1.0,
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

    my_truncation_workflow(client)

    print("--------------------------------")
    print("Done!")


if __name__ == "__main__":
    main()

