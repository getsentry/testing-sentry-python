import os

from huey import RedisHuey

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.huey import HueyIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[
        HueyIntegration(),
        LoggingIntegration(event_level=logging.ERROR, level=None),
    ],
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

huey = RedisHuey("test-huey", host="localhost", port=6379)


@huey.task()
def add_numbers(a, b):
    return a + b


@huey.task(retries=1)
def divide(a, b):
    return a / b
