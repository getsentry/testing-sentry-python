import os
import logging

logger = logging.getLogger('warn.logger')
from flask import Flask

from tasks import my_task

logger = logging.getLogger('warn.logger')

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[
        CeleryIntegration(propagate_traces=False),
        LoggingIntegration(event_level=logging.ERROR, level=None),
    ],
    data_collection={"stack_frame_variables": {"mode": "denylist"}},
    attach_stacktrace=False,
)

from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import EventHandler, LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration

def prepare_event(event, hint):
    return event

already_seen = set()

def sample_errors(event,):
    msg = event["logentry"]["message"]
    if msg not in already_seen:
        already_seen.add(msg)
        return True
    
    return False

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    release="test",
    before_send=prepare_event,
    error_sampler=sample_errors,
    default_integrations=False,
    debug=False,
    integrations=[
        StdlibIntegration(),
        ExcepthookIntegration(),
        DedupeIntegration(),
        AtexitIntegration(),
        ModulesIntegration(),
        LoggingIntegration(breadcrumb_level=None, event_level=logging.WARNING, level=None),
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
app = Flask(__name__)

@app.route("/")
def hello_world():
    my_task.delay()
    return "<p>Hello, World!</p>"


@app.route("/trx")
def flask_transaction():
    return "<p>Hello, World!</p>"



if __name__ == "__main__":
    # from tasks import task_a
    # task_a.delay()
    # raise Exception("Main!")

    for x in range(10):
        try:
            raise RuntimeError('Oh no!')
        except Exception as e:
            logger.warning('Error get value from service', exc_info=True)