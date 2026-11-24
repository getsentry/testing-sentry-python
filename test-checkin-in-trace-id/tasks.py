
from celery import Celery, signals

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# 'python' project on Sentry.io
DSN = "https://2c6ef38b3a00490ba49b4677dbef4db6@o447951.ingest.sentry.io/4505239425777664"

app = Celery('tasks', broker='redis://localhost:6379')

@signals.celeryd_init.connect
def connect_sentry(**kwargs):
    print("------------------connected sentry to celery ------------------------")
    sentry_sdk.init(
        dsn=DSN,
        debug=True,
#        traces_sample_rate=1.0,
        integrations=[
            CeleryIntegration(
                propagate_traces=False,
            ),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ], 
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


@app.task()
def add_together(a, b):
    some_other_task.delay(1, 2)
    raise Exception("222 Error in celery task")
    return a + b


@app.task()
def some_other_task(a, b):
    raise Exception("222 Another Error in celery task")
    return a + b

