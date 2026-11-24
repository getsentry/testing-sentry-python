import os 

from celery import Celery, signals

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration


app = Celery(
    "tasks", 
    broker="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/1",
)


@signals.celeryd_init.connect
def concect_sentry(**kwargs):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        traces_sample_rate=1,
        debug=True,
        integrations=[
            # CeleryIntegration(),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        data_collection={
            "user_info": False,
            "http_bodies": ["incoming_request"],
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
    raise Exception("Something went wrong in the world")


@app.task
def task_b(msg):
    return "[task-b] Hello there %s" % msg
