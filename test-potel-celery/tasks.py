import os
import time
import random
import logging

from celery import Celery, signals
from celery.schedules import crontab

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import logger as sentry_logger
from sentry_sdk.feature_flags import add_feature_flag
from sentry_sdk.consts import VERSION as SENTRY_SDK_VERSION
from sentry_sdk.integrations.celery import CeleryIntegration

DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__)))


app = Celery("tasks", broker='redis://localhost:6379/0')
app.conf.beat_schedule = {
    'task_a_beat': {
        'task': 'tasks.task_a',
        'schedule': crontab(minute='*/1'),
        'args': ('Task A from beat',),
    },
    # 'task_b_beat': {
    #     'task': 'tasks.task_b',
    #     'schedule': crontab(minute='*/1'),
    #     'args': ('Task B from beat',),
    # },
}
app.conf.timezone = 'UTC'


def before_send_transaction(event, hint):
    print(event)
    return event


def _fibonacci(n):
    print(f"fibonacci {n}")
    time.sleep(0.05)

    if n < 0:
        raise ValueError("Incorrect input: n must be non-negative")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return _fibonacci(n-1) + _fibonacci(n-2)


exclude_beat_tasks=[]


@signals.beat_init.connect   # omit this line if you're running beat directly within your worker process
@signals.celeryd_init.connect
def connect_sentry(**kwargs):
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


@app.task(bind=True, max_retries=3, default_retry_delay=5)
def task_a(self, msg):
    print("[task-a] That's my message to the world: %s" % msg)

    user = {
        "id": "testuser",
        "username": "Test User",
    }

    # feature flag
    add_feature_flag("test-flag", True)

    # spans
    with sentry_sdk.start_span(name="test-span-1"):
        with sentry_sdk.start_span(name="test-span-2"):

            # tag
            sentry_sdk.set_tag("test-tag", "test-value")

            # user
            sentry_sdk.set_user(user)

            # breadcrumb
            sentry_sdk.add_breadcrumb(
                category="test-category",
                message="test breadcrumb",
                level="info",
                data={"user": user},
            )

            # context
            sentry_sdk.set_context("test-context", {"text-context-user": user})

            # attachments
            sentry_sdk.add_attachment(bytes=b"Hello Error World", filename="hello-on-error.txt")
            sentry_sdk.add_attachment(bytes=b"Hello Transaction World", filename="hello-on-transaction.txt")

            # logs
            sentry_logger.warning("test log")

            # do some work, so we have a profile
            _fibonacci(5)

            # retry the task once
            # retry_count = self.request.retries
            # if retry_count == 0:
            #     logging.warn("Will retry the task")
            #     self.retry()

            # raise an error
            # raise ValueError("help! an error!")


@app.task
def task_b(msg):
    print("[task-b] Hello there %s" % msg)
    # time.sleep(10)
    raise Exception("Oh no! Abort! Alarm alarm!")
