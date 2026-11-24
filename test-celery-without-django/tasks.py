import os

from celery import Celery, signals

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


# Initializing Celery
app = Celery("tasks", broker="redis://localhost:6379/0")


@signals.worker_init.connect  # run for each worker process starting
# @signals.celeryd_init.connect  # run once when Celery deamon starts (before workers are spawned)
def init_sentry(**_kwargs):
    # Initializing Sentry SDK in the Celery worker process
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        traces_sample_rate=1.0,
        debug=True,
        integrations=[LoggingIntegration(event_level=logging.ERROR, level=None)],
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


# Setup Celery Tasks
@app.task
def add(x, y):
    import logging
    logging.warning("In add task")
    return x + y


@app.task
def message(msg):
    import logging
    logging.warning("In msg task(%s)", msg)
    return msg
