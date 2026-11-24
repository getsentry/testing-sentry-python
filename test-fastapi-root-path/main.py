from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
# from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

def sentry_traces_sampler(sampling_context):
    print(f"Traces sampler called with {sampling_context}")
    print(f'Traces sampler transaction name: "{sampling_context["transaction_context"]["name"]}"')
    return 1

def bla(sampling_context):
    return True

sentry_sdk.init(
    dsn="https://095875278cb642c0860527ed126333a9@o447951.ingest.sentry.io/6618415",  # Project "fastapi" in Sentry
    debug=True,
    release="0.0.0",
    traces_sample_rate=1.0, 
    traces_sampler=sentry_traces_sampler,
    error_sampler=bla,
    # integrations=[
    #     StarletteIntegration(transaction_style="endpoint"),
    #     FastApiIntegration(transaction_style="endpoint"),
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


app = FastAPI(root_path="/api/v1")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/{server_something}")
async def server_api(server_something):
    # sentry_sdk.capture_message("Server received request %s" % server_something)

    1/0

    # with sentry_sdk.configure_scope() as scope:
    #     scope.set_transaction_name(f"test sentry transaction {server_something}")
        
    return {
        "given_by_you": server_something,
        "returned_by_server": server_something.upper(),
    }


@app.post("/post/{server_something}")
async def server_api_post(server_something):
    # sentry_sdk.capture_message("Server received request %s" % server_something)

    # 1/0

    return {
        "given_by_you": server_something,
        "returned_by_server": server_something.upper(),
    }
