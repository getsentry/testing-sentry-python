import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from tasks import task_a, task_b

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),
    traces_sample_rate=1.0,
    debug=True,
    # integrations=[
    # ],
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

origins = [
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "Async World"}


@app.get("/something/{message}")
async def read_something(message: str):
    # task_b.apply_async((message, ), headers={"sentry-propagate-traces": False})
    result = task_b.apply_async((message, ))

    return {"Hello": result.get()}


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

