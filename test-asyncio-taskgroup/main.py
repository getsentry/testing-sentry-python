import asyncio
import json
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


def before_send(event, hint):
    # Drop error events that are from Starlette integration
    # (the -1 index is needed because it is an ExceptionGroup containing multiple exceptions)
    if event["exception"]["values"][-1]["mechanism"]["type"] == "starlette":
        return None

    return event


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),
    environment=os.getenv("ENV", "local"),
    traces_sample_rate=1.0,
    trace_lifecycle="stream",
    debug=True,
    instrumenter="otel",
    before_send=before_send,
    integrations=[
        LoggingIntegration(event_level=None, level=None),
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
        AsyncioIntegration(),
        AioHttpIntegration(),
    ],
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


# Setup Sentry with OpenTelemetry
from opentelemetry import trace
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from sentry_sdk.integrations.opentelemetry import SentrySpanProcessor, SentryPropagator

provider = TracerProvider()
provider.add_span_processor(SentrySpanProcessor())
trace.set_tracer_provider(provider)
set_global_textmap(SentryPropagator())

FastAPIInstrumentor.instrument_app(app)
