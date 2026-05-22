import os

from huey import RedisHuey

import sentry_sdk
from sentry_sdk.integrations.huey import HueyIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[
        HueyIntegration(),
    ],
)

huey = RedisHuey("test-huey", host="localhost", port=6379)


@huey.task()
def add_numbers(a, b):
    return a + b


@huey.task(retries=1)
def divide(a, b):
    return a / b
