import os

import sentry_sdk
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    debug=True,
    _experiments={"trace_lifecycle": "stream"},
)


def index(request):
    return Response("Hello from Pyramid!")


def error(request):
    raise ValueError("help! an error!")


def message(request):
    name = request.matchdict.get("name", "World")
    return Response(f"Hello, {name}!")


def create_app():
    with Configurator() as config:
        config.add_route("index", "/")
        config.add_view(index, route_name="index")

        config.add_route("error", "/error")
        config.add_view(error, route_name="error")

        config.add_route("message", "/message/{name}")
        config.add_view(message, route_name="message")

        app = config.make_wsgi_app()

    return app


if __name__ == "__main__":
    app = create_app()
    print("Serving on http://localhost:8000")
    serve(app, host="0.0.0.0", port=8000)
