import logging
import time
import os

import sentry_sdk
from opentelemetry import trace
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.otlp import OTLPIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[
        OTLPIntegration(setup_propagator=True),
        LoggingIntegration(event_level=logging.ERROR, level=None),
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
    debug=True,
)

tracer = trace.get_tracer(__name__)

# Start a new span
with tracer.start_as_current_span("test_otel_span"):
    with tracer.start_as_current_span("test_otel_span_child"):
        print("Processing some data...")
    # Simulate some processing
    time.sleep(1)
