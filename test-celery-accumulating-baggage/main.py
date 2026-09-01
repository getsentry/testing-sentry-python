import os

import logging

import sentry_sdk
from celery import Celery
from sentry_sdk.integrations.celery import CeleryIntegration

log = logging.getLogger(__name__)

sentry_settings = {
    "dsn": os.getenv("SENTRY_DSN", None),
    "environment": os.getenv("ENV", "local.main"),
    "release": "0.0.0",        
    "traces_sample_rate": 1.0,
    "trace_lifecycle": "stream",
    "send_default_pii": True,
    "debug": True,
    "integrations": [CeleryIntegration(
        propagate_traces=True, 
    )]
}
print(f"Sentry Settings: {sentry_settings}")
sentry_sdk.init(**sentry_settings)

app = Celery(broker='redis://localhost:6379/0')
app.conf.task_always_eager = False


@app.task(name='baggage_issue', bind=True, acks_late=True, default_retry_delay=0, max_retries=5)
def baggage_issue(self):
    with sentry_sdk.start_transaction(name='baggage_issue_task', op="celery", sampled=True):
        baggage = (self.request.headers or {}).get('baggage', '')
        log.warning("XXX")
        log.warning('%s %s', len(baggage), baggage)
        self.retry(countdown=0)


if __name__ == '__main__':
    with sentry_sdk.start_transaction(name='baggage_issue', op="celery", sampled=True):
        baggage_issue.delay()
