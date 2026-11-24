import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from tasks import message


def main():
    # Initializing Sentry SDK in our process
    # This is not the process Celery runs in.
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        traces_sample_rate=1.0,
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

    # Enqueueing a task to be processed by Celery
    with sentry_sdk.start_span(name="calling-a-celery-task"):
        result = message.apply_async(
            args=("This should be connected.", ),
        )
        print(f"Task ID 1: {result.id}")

        result = message.apply_async(
            args=("This should NOT be connected.", ),
            headers={"sentry-propagate-traces": False},
        )
        print(f"Task ID 2: {result.id}")

if __name__ == "__main__":
    main()
