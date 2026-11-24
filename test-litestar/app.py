import os
import time

from litestar import Litestar, get
from litestar.logging.config import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.middleware.session.client_side import CookieBackendConfig


from sentry_sdk.integrations.litestar import LitestarIntegration
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[
        LitestarIntegration(),
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
)


@get("/")
async def index() -> str:
    return "Hello, world!"


@get("/error")
async def error() -> dict[str, int]:
    var1 = 123
    var2 = 0
    bla = var1 / var2
    return {"error": bla}


@get("/books/{book_id:int}")
async def get_book(book_id: int) -> dict[str, int]:
    time.sleep(0.005)
    return {"book_id": book_id}


logging_middleware_config = LoggingMiddlewareConfig()
rate_limit_config = RateLimitConfig(rate_limit=("second", 1), exclude=["/schema"])
session_config = CookieBackendConfig(secret=os.urandom(16))  # type: ignore[arg-type]


app = Litestar(
    route_handlers=[index, get_book, error], 
    logging_config=LoggingConfig(),
    middleware=[
        logging_middleware_config.middleware, 
        rate_limit_config.middleware, 
        session_config.middleware,
    ],
)
