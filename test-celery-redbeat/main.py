import datetime

import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from tasks import task_a, task_b


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "debug": True,
        # "integrations": [],
        "integrations": [LoggingIntegration(event_level=logging.ERROR, level=None)],
        "data_collection": {"stack_frame_variables": {"mode": "denylist"}},
        "attach_stacktrace": False,
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.start_span(name="celery-propagate-traces", attributes={"sentry.op": "function"}):
        import ipdb; ipdb.set_trace()
        task_a.delay("Task A msg 2")
        # task_b.apply_async(("Task B msg", ))
        task_b.apply_async(("Task B msg 2", ), headers={"sentry-propagate-traces": False})


if __name__ == "__main__":
    main()