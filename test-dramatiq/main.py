import os

import dramatiq

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.dramatiq import DramatiqIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    debug=True,
    integrations=[
        DramatiqIntegration(),
        LoggingIntegration(event_level=logging.ERROR, level=None),
    ],
    max_request_body_size="always",
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

from dramatiq.brokers.redis import RedisBroker

redis_broker = RedisBroker(host="localhost", port=6379)
dramatiq.set_broker(redis_broker)

@dramatiq.actor(max_retries=0)
def dummy_actor(x, y):
    return x / y


if __name__ == "__main__":
    # dummy_actor(1, 2)
    # dummy_actor.send(3, 4)
    dummy_actor.send(12, 0)
