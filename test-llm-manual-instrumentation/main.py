import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def main():
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=1.0,
        debug=True,
        integrations=[LoggingIntegration(event_level=logging.ERROR, level=None)],
        data_collection={
            "user_info": False,
            "http_bodies": [],
            "graphql": {"document": False, "variables": False},
            "gen_ai": {"inputs": False, "outputs": False},
            "mcp": {"inputs": False, "outputs": False},
            "database_query_data": False,
            "queues": False,
            "http_headers": {"request": {"mode": "denylist", "terms": ["forwarded", "-ip", "remote-", "via", "-user"]}},
            "cookies": {"mode": "denylist", "terms": ["forwarded", "-ip", "remote-", "via", "-user"]},
            "url_query_params": {"mode": "denylist", "terms": ["forwarded", "-ip", "remote-", "via", "-user"]},
            "stack_frame_variables": {"mode": "denylist"},
        },
        attach_stacktrace=False,
    )

    pipeline_name = "My AI pipeline"

    with sentry_sdk.start_span(name="main", attributes={"sentry.op": "main"}):  # thats the transaction created by FastAPI (or other framework)
        with sentry_sdk.start_span(name=pipeline_name, attributes={"sentry.op": "ai.pipeline"}):
            with sentry_sdk.start_span(name="some-other-span", attributes={"sentry.op": "some-other-span"}):  # simulating span from other integrations.
                for i in range(5):
                    with sentry_sdk.start_span(name="My Chat completion", attributes={"sentry.op": "ai.chat_completions.create.openai"}) as span:
                        span.set_attribute("ai.input_messages", ["Hello, how are you?"])
                        span.set_attribute("ai.model_id", "ai-007")
                        span.set_attribute("ai.streaming", True)
                        span.set_attribute("ai.responses", ["I'm fine", "Thank you!"])
                        span.set_attribute("ai.pipeline.name", pipeline_name)

                        span.set_attribute("ai_completion_tokens_used", 7)
                        span.set_attribute("ai_prompt_tokens_used", 6)
                        span.set_attribute("ai_total_tokens_used", 13)


if __name__ == "__main__":
    main()