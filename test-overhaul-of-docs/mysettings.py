# mysettings.py
import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_settings = {
    "dsn": os.getenv("SENTRY_DSN", None),
    "environment": os.getenv("ENV", "local"),
    "traces_sample_rate": 1.0,
    # "send_default_pii": True,
    "debug": True,
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
