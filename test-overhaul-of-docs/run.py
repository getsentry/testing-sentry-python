import os

import asyncio

from arq import create_pool
from arq.connections import RedisSettings

import sentry_sdk
from sentry_sdk.integrations.arq import ArqIntegration


async def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        # "send_default_pii": True,
        "debug": True,
        "trace_lifecycle": "stream",
        "integrations": [ArqIntegration()],
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    redis = await create_pool(RedisSettings())

    with sentry_sdk.start_transaction(name="testing_sentry"):
        r = await redis.enqueue_job("add_numbers", 1, 2)

asyncio.run(main())