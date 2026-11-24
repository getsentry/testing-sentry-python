import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    integrations=[
        StarletteIntegration(middleware_spans=False),
        LoggingIntegration(event_level=logging.ERROR, level=None),
    ],
    debug=True,
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


def generate_response():
    with sentry_sdk.start_span(name="SPAN Stream Response Generator", attributes={"sentry.op": "demo.function"}) as span:
        print(f"SPAN START generator: {span}")
        span.set_attribute("more", "value")
        for i in range(3):
            with sentry_sdk.start_span(name="Stream Chunk", attributes={"sentry.op": "demo.function"}) as span2:
                print(f"SPAN START chunk: {span2}")
                yield f"Hello, {i} World!\n"

            print(f"SPAN END chunk: {span2.start_timestamp} -> {span2.timestamp}")

    print(f"SPAN END generator: {span.start_timestamp} -> {span.timestamp}")


@app.get("/")
def hello() -> str:
    with sentry_sdk.start_span(name="SPAN Streaming View", attributes={"sentry.op": "demo.function"}) as span:
        print(f"SPAN START view: {span}")
        span.set_attribute("some", "value")
        print(span)
        output = StreamingResponse(generate_response(), media_type='text/event-stream')

    print(f"SPAN END view: {span.start_timestamp} -> {span.timestamp}")
    return output
