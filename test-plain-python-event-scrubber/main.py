import asyncio
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


PII_DENYLIST = ["card_details"]


def scrub_span(span, hint):
    attributes = span.get("attributes", {})
    for key in PII_DENYLIST:
        if key in attributes:
            attributes[key] = "[Filtered]"
    return span


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        before_send_span=scrub_span,
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
            "stack_frame_variables": False,
        },
        attach_stacktrace=False,
        debug=True,
    )

    with sentry_sdk.start_span(name="test-transaction", attributes={"sentry.op": "function"}) as trx:
        trx.set_attribute("card_details", "2222420000001113")  # tags are NOT scrubbed...
        print("Hello, world!")

if __name__ == "__main__":
    asyncio.run(main())
