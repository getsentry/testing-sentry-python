import os
import random
import time

from flask import Flask
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),
    environment="development",
    release="unknown",
    traces_sample_rate=1.0,
    enable_db_query_source=True,
    db_query_source_threshold_ms=0,
    debug=True,
    integrations=[LoggingIntegration(event_level=logging.ERROR, level=None)],
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
def stream_response():
    num = random.randint(1, 100)
    sentry_sdk.set_tag(f"tag_num", num)

    def generate():
        for _ in range(100):
            yield f"{num}_{_}|"
            if _ % 100 == 0:
                time.sleep(0.1)
                yield "\n"
                print(num)

        1 / 0

    return generate(), {"Content-Type": "text/plain"}
