import os

import sentry_sdk
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration


sentry_sdk.init(
    dsn="",
    environment=os.environ.get("ENV", "test"),
    _experiments={"trace_lifecycle": "stream"},
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    debug=True,
    integrations=[
        AioHttpIntegration(),
    ],
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
