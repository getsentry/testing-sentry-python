# tasks.py
import os 
import logging
import time
from secrets import token_hex

from celery import Celery
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[LoggingIntegration(event_level=logging.ERROR, level=None)],
    data_collection={"stack_frame_variables": {"mode": "denylist"}},
    attach_stacktrace=False,
)

app = Celery("tasks", broker='redis://localhost:6379/0')
logger = logging.getLogger(__name__)

logger.error(f"SETUP {token_hex(2)}")

@app.task
def my_task():
    msg = f"MY_TASK2 {token_hex(2)}"
    logging.info(msg)
    logger.error(msg)
    time.sleep(1)