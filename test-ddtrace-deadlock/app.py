import logging
import os
import time

from flask import Flask

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    traces_sample_rate=1.0,
    integrations=[
        LoggingIntegration(
            breadcrumb_level=logging.INFO,
            event_level=logging.INFO,
            level=None,#WARNING,
        ),
    ],
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    debug=True,
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

logging.info('Flask app initialized')


@sentry_sdk.trace
def fibonacci(n):
    time.sleep(0.01)
    if n < 0:
        print("Incorrect input")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)


@app.route("/")
def index():
    logging.info('Flask index route called')
    with sentry_sdk.start_span(name="test"):
        fibonacci(10)
        return {"message": "Hello, World!"}


@app.route('/favicon.ico')
def favicon():
    logging.info('Flask favicon route called')
    return '', 204
