import os

import pyspark.daemon as original_daemon

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.spark.spark_worker import SparkWorkerIntegration


if __name__ == '__main__':
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[
            SparkWorkerIntegration(), 
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
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
    
    # Do not print anything here - it interferes with Spark's daemon communication
    
    # Call the original daemon manager
    original_daemon.manager()
