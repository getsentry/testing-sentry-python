import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.consts import VERSION as SENTRY_SDK_VERSION
from sentry_sdk.integrations.celery import CeleryIntegration

from tasks import task_a, task_b, before_send_transaction

DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

exclude_beat_tasks = []


def main():
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=f"{DIR}-{SENTRY_SDK_VERSION}",
        release=SENTRY_SDK_VERSION,
        integrations=[
            CeleryIntegration(monitor_beat_tasks=True, exclude_beat_tasks=exclude_beat_tasks),
            LoggingIntegration(event_level=logging.ERROR),
        ],
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        debug=True,
        spotlight="http://localhost:9999/api/0/envelope/",
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    with sentry_sdk.start_span(name="celery-task-started-from-transaction", attributes={"sentry.op": "function"}):
        task_a.delay("Task A from main (via delay)")
        # task_b.apply_async(("Task B from main (via apply_async)", ), headers={"sentry-propagate-traces": False})


if __name__ == "__main__":
    main()
