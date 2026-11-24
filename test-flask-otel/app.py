import logging
import os
from random import randint

from flask import Flask, request

from opentelemetry import trace

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.otlp import OTLPIntegration


sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    # send OpenTelemetry spans to Sentry instead of using Sentry's own tracing
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

# Acquire a tracer
tracer = trace.get_tracer("diceroller.tracer")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/rolldice")
def roll_dice():
    player = request.args.get("player", default=None, type=str)
    result = str(roll())
    if player:
        logger.warn("%s is rolling the dice: %s", player, result)
    else:
        logger.warn("Anonymous player is rolling the dice: %s", result)
    return result


def roll():
    # This creates a new span that's the child of the current one
    with tracer.start_as_current_span("roll") as rollspan:
        res = randint(1, 6)
        rollspan.set_attribute("roll.value", res)
        return res
