import datetime 
import os 

from celery import Celery, signals

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration


app = Celery("tasks", broker='redis://localhost:6379/0')
app.conf.timezone = 'Europe/London'
app.conf.beat_schedule = {
    'task-a-from-beat': {
        'task': 'tasks.task_a',
        'schedule': datetime.timedelta(minutes=1), #crontab(hour='*', minute='*'),
        'args': ("TASK A from beat", ),
    },
}


@signals.celeryd_init.connect
def concect_sentry(**kwargs):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        # integrations=[
        #     CeleryIntegration(),
        # ],
        environment="dev.celery",
        release="0.0.0",
        traces_sample_rate=1,
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


@app.task
@sentry_sdk.monitor(monitor_slug='anton-task-a')
def task_a(msg):
    # with sentry_sdk.start_transaction(op="function", name="task-a"):
    print("[task-a] That's my message to the world: %s" % msg)
    for x in range(1):
        task_b.delay("Task B number {}".format(x))

    # raise Exception("Something went wrong in the world")


@app.task
# @sentry_sdk.monitor(monitor_slug='anton-task-b') 
def task_b(msg):
    # with sentry_sdk.start_transaction(op="function", name="task-b"):
    # import time
    # time.sleep(0.1)
    print("[task-b] Hello there %s" % msg)
    # raise Exception("Oh no! Abort! Alarm alarm!")

