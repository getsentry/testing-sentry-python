import os
from loguru import logger as loguru_logger

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        LoguruIntegration(
            breadcrumb_level="TRACE",
            event_level="ERROR",
            level=None,
        ),
        LoggingIntegration(event_level=logging.ERROR, level=None),
    ],
    traces_sample_rate=1.0,
    debug=True,
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


@loguru_logger.catch
def my_function(x, y, z):
    # An error? It's caught anyway!
    return 1 / (x + y + z)


def main():
    loguru_logger.trace("{}: I am a {level_str} event", "Guru", level_str="TRACE")
    loguru_logger.debug("{}: I am a {level_str} event", "Guru", level_str="DEBUG")
    loguru_logger.info("{}: I am a {level_str} event", "Guru", level_str="INFO")
    loguru_logger.success("{}: I am a {level_str} event", "Guru", level_str="SUCCESS")
    loguru_logger.warning("{}: I am a {level_str} event", "Guru", level_str="WARNING")
    loguru_logger.error("{}: I am a {level_str} event", "Guru", level_str="ERROR")
    loguru_logger.critical("{}: I am a {level_str} event", "Guru", level_str="CRITICAL")

    new_level = loguru_logger.level("SNAKY", no=38, color="<yellow>", icon="🐍")
    loguru_logger.log("SNAKY", "{}: I am a {level_str} event", "Guru", level_str="SNAKY")

    try:
        1 / 0
    except ZeroDivisionError:
        loguru_logger.exception("{}: An exception happened!", "Guru")


if __name__ == "__main__":
    main()