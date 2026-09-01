import os 
import time
import random

from celery import Celery, signals
from celery.schedules import crontab

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration


CELERY_BROKER_REDIS = "redis://localhost:6379/0"
CELERY_BROKER_RABBITMQ = "amqp://guest:guest@localhost:5672"


app = Celery("tasks", broker_url=CELERY_BROKER_RABBITMQ)
app.conf.timezone = 'UTC'


@signals.celeryd_init.connect
def connect_sentry(**kwargs):
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "celery.consumer"),
        "release": "0.0.0",
        "traces_sample_rate": 1.0,
        "trace_lifecycle": "stream",
        "send_default_pii": True,
        "debug": True,
        "integrations": [CeleryIntegration()],
    }
    print(f"Sentry Settings: {sentry_settings}")
    sentry_sdk.init(**sentry_settings)


@app.task
def task_a(msg):
    print("[task-a] That's my message to the world: %s" % msg)


@app.task
def task_b(msg):
    print("[task-b] Hello there %s" % msg)
    # time.sleep(10)
    # raise Exception("Oh no! Abort! Alarm alarm!")
