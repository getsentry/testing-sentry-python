import datetime

import os

import sentry_sdk

from tasks import task_a, task_b


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "trace_lifecycle": "stream",
        "send_default_pii": True,
        "debug": True,
        # "integrations": [],
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.start_transaction(op="function", name="celery-max-tasks-per-child"):
        task_a.delay("Task A, the mother of all tasks")
        # task_b.apply_async(("Task B msg 2", ), headers={"sentry-propagate-traces": False})

if __name__ == "__main__":
    main()