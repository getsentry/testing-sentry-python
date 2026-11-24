import asyncio
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        debug=True,
        max_breadcrumbs=3,
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

    with sentry_sdk.start_span(name="test-transaction", attributes={"sentry.op": "function"}):
        logger.info("breadcrumb 1", extra=dict(foo=42, password="secret"))
        logger.info("breadcrumb 2", extra=dict(foo=1, password="secret"))
        logger.info("breadcrumb 3", extra=dict(bar=2, auth="secret"))
        logger.info("breadcrumb 4", extra=dict(foobar=3, password="secret"))
        logger.info("breadcrumb 5", extra=dict(foobar=45, password="secret"))
        # only the last 3 breadcrumbs are sent
        logger.critical("whoops", extra=dict(bar=69, auth="secret"))


if __name__ == "__main__":
    asyncio.run(main())
