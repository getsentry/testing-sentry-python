import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.traces
from sentry_sdk.integrations.celery import CeleryIntegration

from tasks import task_a, task_b, before_send_span

exclude_beat_tasks = []


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local.main"),
        "release": "0.0.0",        
        "traces_sample_rate": 1.0,
        "debug": True,
        "integrations": [
            CeleryIntegration(monitor_beat_tasks=True, exclude_beat_tasks=exclude_beat_tasks),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        "before_send_span": before_send_span,
        "data_collection": {"stack_frame_variables": {"mode": "denylist"}},
        "attach_stacktrace": False,
    }
    print(f"Sentry Settings: {sentry_settings}")
    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.traces.start_span(name="celery-task-started-from-transaction", attributes={"sentry.op": "function"}):
        task_a.delay("Task A from main (via delay)")
        # task_b.apply_async(("Task B from main (via apply_async)", ), headers={"sentry-propagate-traces": False})


if __name__ == "__main__":
    main()