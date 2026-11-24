import os 

from celery import Celery, signals

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration


app = Celery("tasks", broker='redis://localhost:6379/0')

def before_send_span(span, hint):
    print(span)
    return span

exclude_beat_tasks = []

@signals.celeryd_init.connect
def concect_sentry(**kwargs):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        integrations=[
            CeleryIntegration(monitor_beat_tasks=True, exclude_beat_tasks=exclude_beat_tasks),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        environment="dev.celery",
        release="0.0.0",
        traces_sample_rate=1,
        debug=True,
        before_send_span=before_send_span,
        data_collection={
            "user_info": False,
            "http_bodies": [],
            "graphql": {"document": False, "variables": False},
            "gen_ai": {"inputs": False, "outputs": False},
            "mcp": {"inputs": False, "outputs": False},
            "database_query_data": False,
            "queues": False,
            "http_headers": {"request": {"mode": "denylist", "terms": ["forwarded", "-ip", "remote-", "via", "-user"]}},
            "cookies": {"mode": "denylist", "terms": ["forwarded", "-ip", "remote-", "via", "-user"]},
            "url_query_params": {"mode": "denylist", "terms": ["forwarded", "-ip", "remote-", "via", "-user"]},
            "stack_frame_variables": {"mode": "denylist"},
        },
        attach_stacktrace=False,
    )


@app.task
def task_a(msg):
    print("[task-a] That's my message to the world: %s" % msg)
    import time
    time.sleep(0.05)
    # raise Exception("Something went wrong in the world")


@app.task
def task_b(msg):
    print("[task-b] Hello there %s" % msg)
    raise Exception("Oh no! Abort! Alarm alarm!")
