import os

import aiohttp

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from utils import format_baggage

def traces_sampler(sampling_context):
    return 0.111

# *** SENTRY INITIALIZATION ***

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN_BACKEND1"),
    environment=os.environ.get("SENTRY_ENVIRONMENT"),
    release="backend1@0.0.1",
    traces_sample_rate=1,
    traces_sampler=traces_sampler,
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


app = FastAPI()


# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["sentry-trace", "baggage"]  # Expose both sentry-trace and baggage headers
)


@app.middleware("http")
async def test_middleware(request, call_next):
    return await call_next(request)


@app.get("/test1")
async def backend1_endpoint(request: Request):
    print("\nIncoming request (from frontend):")
    print(f"- sentry-trace: {request.headers.get('sentry-trace')}")
    print(f"- baggage: {request.headers.get('baggage')}")
    print(format_baggage(request.headers.get('baggage')))

    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8002/test2') as response:
            print("\nOutgoing request (to backend2):")
            print(f"- sentry-trace: {response.request_info.headers.get('sentry-trace')}")
            print(f"- baggage: {response.request_info.headers.get('baggage')}")
            print(format_baggage(response.request_info.headers.get('baggage')))

            return {
                "iam": "backend1",
                "received": await response.json()
            }
