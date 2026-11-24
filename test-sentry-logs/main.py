import os
import random

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.logger


def before_log(record, hint):
    if record['severity_text'] == 'fatal':
        return None

    return record


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    debug=True,
    before_send_log=before_log,
    integrations=[LoggingIntegration(event_level=logging.ERROR)],
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


def main():
    for x in range(1000):
        sentry_sdk.logger.trace("This is a 'trace' log...{rand}", rand=random.randint(0, 100))
        sentry_sdk.logger.debug("This is a 'debug' log... ({rand})", rand=random.randint(0, 100), bla="asdfoamsdfl")
        sentry_sdk.logger.info("This is a 'info' log... ({rand})", rand=random.randint(0, 100))
        sentry_sdk.logger.warning("This is a 'warn' log... ({rand})", rand=random.randint(0, 100))
        sentry_sdk.logger.error("This is a 'error' log... ({rand})", rand=random.randint(0, 100))
        sentry_sdk.logger.fatal("This is a 'fatal' log... ({rand})", rand=random.randint(0, 100))


if __name__ == '__main__':
    main()
