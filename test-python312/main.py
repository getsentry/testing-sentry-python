import os
import signal
import time

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def signal_handler(sig, frame):
    print("SIGINT received")
    sentry_sdk.capture_message("SIGINT received")

    with sentry_sdk.start_span(name="xxxpython312") as transaction:
        transaction.status = "ok"
        for x in range(10):
            with sentry_sdk.start_span(name=f"xxxchild{x} descriptions") as span:
                span.set_attribute("x", x)

    import sys
    sys.exit(0)


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        # "send_default_pii": True,
        "debug": True,
        # "integrations": [],
        "integrations": [LoggingIntegration(event_level=logging.ERROR, level=None)],
        "data_collection": {
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
        "attach_stacktrace": False,
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    signal.signal(signal.SIGINT, signal_handler)
    
    with sentry_sdk.start_span(name="python312") as transaction:
        transaction.status = "ok"
        for x in range(10):
            with sentry_sdk.start_span(name=f"child{x} descriptions") as span:
                span.set_attribute("x", x)

    time.sleep(10)


if __name__ == "__main__":
    main()
