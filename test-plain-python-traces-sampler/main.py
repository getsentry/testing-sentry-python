import asyncio
import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def traces_sampler(sampling_context):
    import ipdb; ipdb.set_trace()
    print(f"Traces sampler called with {sampling_context}")
    print(f'Traces sampler transaction name: "{sampling_context["transaction_context"]["name"]}"')

    transaction = sampling_context.get("transaction_context")
    if transaction:
        transaction["tags"] = {
            "testxxx-tag": "testxxx-value",
        }
        
    return 1

async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        traces_sampler=traces_sampler,
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

    with sentry_sdk.start_span(name="transaction-with-traces-sampler-data", attributes={"sentry.op": "function"}):
        print("Hello, world!")

if __name__ == "__main__":
    asyncio.run(main())