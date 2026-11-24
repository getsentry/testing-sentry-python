import os

from fastapi import FastAPI, Depends

from starlette.types import Receive, Scope, Send
from starlette.middleware import Middleware

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
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


class LoggingMiddleware:
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        self.name = args[0]
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...


app = FastAPI(
    middleware=[
        Middleware(LoggingMiddleware, "app.request"),
    ],
)


def get_user():
    user = {
      "id": "testuser"
    }
    sentry_sdk.set_user(user)
    return user


@app.middleware("http")
async def test_middleware(request, call_next):
    print("middleware")
    return await call_next(request)


@app.get("/error")
def endpoint(user = Depends(get_user)):
    raise ValueError("help! an error!")


@app.get("/")
def endpoint():
    return {
        "hello": "world!",
        "errors-are-here": "http://localhost:5000/error",
    }
