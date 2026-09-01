import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from tasks import task_a, task_b


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "celery.producer"),
        "release": "0.0.0",        
        "traces_sample_rate": 1.0,
        "trace_lifecycle": "stream",
        "send_default_pii": True,
        "debug": True,
        "integrations": [CeleryIntegration()]
    }
    print(f"Sentry Settings: {sentry_settings}")
    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.start_transaction(op="function", name="celery-task-started-from-transaction"):
        task_a.delay("Task A from main (via delay)")
        task_b.apply_async(("Task B from main (via apply_async)", ), headers={"sentry-propagate-traces": False})


if __name__ == "__main__":
    main()