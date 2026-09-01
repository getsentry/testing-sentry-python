# tasks.py
import os 
import logging
import time
from secrets import token_hex

from celery import Celery
from celery.schedules import crontab
from celery import shared_task

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    enable_tracing=True,
    trace_lifecycle="stream",
    debug=True,
    send_default_pii=True,
    integrations=[
        CeleryIntegration(propagate_traces=False)
    ]
)

app = Celery("tasks", broker='redis://localhost:6379/0')
app.conf.beat_schedule = {
    'my_task_from_beat': {
        'task': 'tasks.my_task',
        'schedule': crontab(minute='*/1'),
        'args': ('BEAT',),
    },
}
app.conf.timezone = 'UTC'


logger = logging.getLogger(__name__)

# logger.error(f"SETUP {token_hex(2)}")

@shared_task
def my_task(msg=""):
    sentry_sdk.capture_message('Results!', level='fatal')
    msg = f"{msg} MY_TASK3 {token_hex(2)}"
    logging.info(msg)
    logger.error(msg)
    time.sleep(1)


@app.task
def task_a():
    task_b.delay()
    raise Exception("Task A")

@app.task
def task_b():
    raise Exception("Task B")