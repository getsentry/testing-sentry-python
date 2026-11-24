import os
import time

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from fastapi import FastAPI, BackgroundTasks


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


app = FastAPI()


async def write_notification(email: str, message=""):
    with sentry_sdk.start_span(name=f"Notification for {email}", attributes={"sentry.op": "write_notification"}):
        time.sleep(0.1)
        print(f"Notification for {email}: {message}")


@app.get("/")
async def index(background_tasks: BackgroundTasks):
    for x in range(5):
        background_tasks.add_task(write_notification, x, message="some notification")

    return {"message": "Notification sent in the background"}