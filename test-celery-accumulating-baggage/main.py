import os

import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from celery import Celery
from sentry_sdk.integrations.celery import CeleryIntegration

log = logging.getLogger(__name__)

sentry_settings = {
    "dsn": os.getenv("SENTRY_DSN", None),
    "environment": os.getenv("ENV", "local.main"),
    "release": "0.0.0",        
    "traces_sample_rate": 1.0,
    "debug": True,
    "integrations": [CeleryIntegration(
        propagate_traces=True, 
    ), LoggingIntegration(event_level=logging.ERROR, level=None)],
    "data_collection": {"stack_frame_variables": {"mode": "denylist"}},
    "attach_stacktrace": False,
}
print(f"Sentry Settings: {sentry_settings}")
sentry_sdk.init(**sentry_settings)

app = Celery(broker='redis://localhost:6379/0')
app.conf.task_always_eager = False


@app.task(name='baggage_issue', bind=True, acks_late=True, default_retry_delay=0, max_retries=5)
def baggage_issue(self):
    with sentry_sdk.start_span(name='baggage_issue_task', attributes={"sentry.op": "celery"}):
        baggage = (self.request.headers or {}).get('baggage', '')
        log.warning("XXX")
        log.warning('%s %s', len(baggage), baggage)
        self.retry(countdown=0)


if __name__ == '__main__':
    with sentry_sdk.start_span(name='baggage_issue', attributes={"sentry.op": "celery"}):
        baggage_issue.delay()
