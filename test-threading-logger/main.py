import logging
import os
import threading
import time

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger("sentry.errors")


def thread_function(name):
    logger.info("Thread %s: starting", name)

    while True:
        logger.exception("There is an error in thread %s!", name)

    
class _TestTransport(sentry_sdk.transport.Transport):
    def capture_envelope(self, event):
        pass
        

if __name__ == "__main__":
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=os.environ.get("ENV", "test"),
        # Set rate to 1.0 to capture 100%
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        debug=True,
        transport=_TestTransport(),
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

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    

    t1 = threading.Thread(target=thread_function, args=(1,), daemon=True)
    t2 = threading.Thread(target=thread_function, args=(2,), daemon=True)
    t3 = threading.Thread(target=thread_function, args=(3,), daemon=True)
    t4 = threading.Thread(target=thread_function, args=(4,), daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()

    # x.join()

    import time
    time.sleep(10)

    logger.info("Main    : all done")
