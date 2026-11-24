import time

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def main():
    sentry_sdk.init(
        dsn="https://d655584d05f14c58b86e9034aab6817f@o447951.ingest.sentry.io/5461230",  # sentry-python on Sentry.io
        traces_sample_rate=1.0,
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

    with sentry_sdk.start_span(name='outer') as outer:
        time.sleep(0.1)
        inner1 = sentry_sdk.start_span(name='inner1', active=False)
        time.sleep(0.2)
        inner2 = sentry_sdk.start_span(name='inner2', active=False)
        time.sleep(0.3)

        with sentry_sdk.start_span(name='inner3'):
            time.sleep(0.4)
            inner_inner = sentry_sdk.start_span(name='innerInner', active=False)
            time.sleep(0.5)
            inner_inner.end()
        
        inner1.end()
        inner2.end()

        outer.set_attribute('outer_duration', 1500)
        

if __name__ == "__main__":
    main()