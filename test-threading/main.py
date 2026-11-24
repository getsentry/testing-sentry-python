import os
import random
import threading
import time

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


@sentry_sdk.trace
def my_function(id):
    print("Function: starting")
    time.sleep(random.randint(0,3))
    sentry_sdk.add_breadcrumb(message=f"my_function({id}): doing something", category="function", level="info")
    

def thread_function(id):
    print("Thread: starting")
    time.sleep(random.randint(0,2))
    sentry_sdk.add_breadcrumb(message=f"thread_function({id}): doing something", category="function", level="info")
    my_function(id)


if __name__ == "__main__":
    print("Main: starting")
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENV", "test"),
        # Set rate to 1.0 to capture 100%
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        debug=True,
        integrations=[LoggingIntegration(event_level=logging.ERROR, level=None)],
        data_collection={
            "user_info": False,
            "http_bodies": [],
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

    with sentry_sdk.start_span(name="main-transaction", attributes={"sentry.op": "transaction"}):
        sentry_sdk.add_breadcrumb(message=f"main(): starting threads", category="function", level="info")
        threads = []

        for i in range(5):
            t = threading.Thread(target=thread_function, name=f"mythread{i}", args=(i, ), daemon=True)   
            threads.append(t)

            t.start()
            sentry_sdk.add_breadcrumb(message=f"main(): thread {i} started", category="function", level="info")

        for t in threads:
            t.join()
            sentry_sdk.add_breadcrumb(message=f"main(): thread {t} joined", category="function", level="info")

        sentry_sdk.add_breadcrumb(message=f"main(): all threads joined", category="function", level="info")

    raise ValueError("Last minute error")
    print("Main: all done")
