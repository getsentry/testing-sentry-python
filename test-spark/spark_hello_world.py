import os
import time

from pyspark.sql import SparkSession

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.spark import SparkIntegration
from sentry_sdk.integrations.spark.spark_worker import SparkWorkerIntegration

###
# This file is the Spark Driver (I think)
###

# Import worker functions
from worker_function import successful_task, failing_task

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        SparkIntegration(),
        SparkWorkerIntegration(),
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

# Create a Spark session (this runs on the driver)
spark = SparkSession.builder \
    .appName("SparkSentryTest") \
    .config("spark.python.worker.reuse", "true") \
    .config("spark.python.use.daemon", "true") \
    .config("spark.python.daemon.module", "sentry_daemon") \
    .getOrCreate()

# Add the sentry_daemon.py to worker's Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sentry_daemon_path = os.path.join(script_dir, "sentry_daemon.py")
spark.sparkContext.addPyFile(sentry_daemon_path)

try:
    # Create batches of data to process
    batches = [
        range(1, 15),
        range(15, 30),
        range(30, 45),
        range(45, 60),
        range(60, 75),
        range(75, 90),
        range(90, 105),
        range(105, 120),
        range(120, 135),
        range(135, 150),
    ]

    for batch in batches:
        rdd = spark.sparkContext.parallelize(batch)

        # print("\n=== Running successful tasks (on workers) ===")
        # start_time = time.time()
        # results = rdd.map(successful_task).collect()
        # duration = time.time() - start_time
        # print(f"Batch processing time: {duration:.2f} seconds")
        # for result in results:
        #     print(f"Result (successful_task): {result}")

        print("\n=== Running tasks with errors (on workers) ===")
        start_time = time.time()
        results = rdd.map(failing_task).collect()
        duration = time.time() - start_time
        print(f"Batch processing time: {duration:.2f} seconds")
        for result in results:
            print(f"Result (failing_task): {result}")
finally:
    # Always stop the Spark session
    spark.stop()
    print("Spark session stopped")