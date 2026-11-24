import asyncio
import os
import redis.asyncio as redis


import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration


def init_sentry():  
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        traces_sample_rate=1.0,
        debug=True,
        integrations=[
            RedisIntegration(
                cache_prefixes=["key1", "key3", "key5", "key7", "key9"]
            ), 
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )


async def main():
    init_sentry()

    r = redis.Redis(host='localhost', port=6379)

    with sentry_sdk.start_span(name="testing_async_redis"):
        await r.set("key1", "foo")
        await r.get("key1")
        await r.set("key2", "foo2")
        await r.get("key2")

asyncio.run(main())
