import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
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
