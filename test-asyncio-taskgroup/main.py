import asyncio
import json
import logging
import os
import random

import aiohttp
import fastapi
from fastapi.responses import StreamingResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.otlp import OTLPIntegration


def before_send(event, hint):
    # Drop error events that are from Starlette integration
    # (the -1 index is needed because it is an ExceptionGroup containing multiple exceptions)
    if event["exception"]["values"][-1]["mechanism"]["type"] == "starlette":
        return None

    return event


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),
    environment=os.getenv("ENV", "local"),
    debug=True,
    before_send=before_send,
    integrations=[
        OTLPIntegration(setup_propagator=True),
        LoggingIntegration(breadcrumb_level=None, event_level=None, level=None),
        StarletteIntegration(),
        FastApiIntegration(),
        AsyncioIntegration(),
        AioHttpIntegration(),
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


app = fastapi.FastAPI()


# Generator function that yields fake text messages from LLM
async def fake_ai_streaming_response():
    for i in range(100):
        print(" x ")

        yield b"some fake text message from LLM"

        await asyncio.sleep(0.1)

        # make some dummy http requests
        async with aiohttp.ClientSession() as session:
            async with session.get('http://google.com') as response:
                print(f" o {response.status}")

                # sometimes raise an error
                if i > 50 and random.random() < 0.1:
                    content = await response.text() # this is probably HTML ...
                    json.loads(content)  # ... thus this will fail


# Stream Response Endpoint
@app.get("/")
async def main():
    return StreamingResponse(fake_ai_streaming_response())


FastAPIInstrumentor.instrument_app(app)
