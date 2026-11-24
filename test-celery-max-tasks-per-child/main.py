import datetime

import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.traces

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

    with sentry_sdk.traces.start_span(
        name="celery-max-tasks-per-child", attributes={"sentry.op": "function"}
    ):
        task_a.delay("Task A, the mother of all tasks")
        # task_b.apply_async(("Task B msg 2", ), headers={"sentry-propagate-traces": False})

if __name__ == "__main__":
    main()