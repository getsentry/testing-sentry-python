import logging
import os
import time

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import FastAPI, Request, Response
from starlette.middleware import Middleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.types import ASGIApp


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, logger_name: str, app: ASGIApp, dispatch: DispatchFunction | None = None
    ):
        super().__init__(app, dispatch)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        self.logger.info("Request open")

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        self.logger.info(f"Request close {duration=}")
        return response


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


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    middleware=[
        Middleware(RequestLoggerMiddleware, "app.request", dispatch=None),
    ],
)


@app.get("/")
def hello() -> str:
    return "Hello World!"