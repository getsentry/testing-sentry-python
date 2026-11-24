import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[
        AioHttpIntegration(),
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


async def index(request):
    return web.json_response(
        {
            "hello": "world!",
            "error": "http://localhost:5000/error",
            "http-error": "http://localhost:5000/http-error",
        }
    )


async def error(request):
    sentry_sdk.set_user({"id": "testuser"})
    raise ValueError("help! an error!")


async def http_error(request):
    raise web.HTTPInternalServerError(reason="something went wrong")


@web.middleware
async def test_middleware(request, handler):
    print("middleware")
    return await handler(request)


def make_app():
    app = web.Application(middlewares=[test_middleware])
    app.router.add_get("/", index)
    app.router.add_get("/error", error)
    app.router.add_get("/http-error", http_error)
    return app


if __name__ == "__main__":
    web.run_app(make_app(), port=5000)
