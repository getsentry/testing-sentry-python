import os
import time

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

from werkzeug.test import Client


def main():
    def generate_content():
        # This response will take 1.5 seconds to generate
        for _ in range(15):
            with sentry_sdk.start_span(name=f"sleep {_}", attributes={"sentry.op": "function"}):
                time.sleep(0.1)
                yield "ok"

    def long_running_app(environ, start_response):
        start_response("200 OK", [])
        return generate_content()

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
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

    app = SentryWsgiMiddleware(long_running_app)

    client = Client(app)
    response = client.get("/")
    _ = response.get_data()


if __name__ == "__main__":
    main()

