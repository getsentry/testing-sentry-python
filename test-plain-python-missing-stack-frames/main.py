import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import capture_exception

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    traces_sample_rate=1.0,
    debug=True,
    add_full_stack=True,
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


def main():
    foo()


def foo():
    try:
        bar()
    except Exception as e:
        capture_exception(e)


def bar():
    raise Exception("This is a test exception")


if __name__ == "__main__":
    main()


# stack sollte sein?:
# line 25
# line 19
# line 14
# line 29


# but instead is:
# line 25
# line 19