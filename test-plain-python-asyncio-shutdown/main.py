import asyncio
import os
import signal
import sys

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration


async def long_running_task():
    try:
        print("Task started")
        await asyncio.sleep(30)
        print("Task completed")
    except asyncio.CancelledError:
        print("Task was cancelled, but ignoring cancellation")
        await asyncio.sleep(10)
        print("Task completed despite cancellation")


async def main():
    # Initialize Sentry with the AsyncioIntegration
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        integrations=[AsyncioIntegration(), LoggingIntegration(event_level=logging.ERROR, level=None)],
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

    # Start a long-running task without keeping a reference to it
    # This is key - we create a "fire and forget" task
    asyncio.create_task(long_running_task())
    
    # Set up a signal handler to initiate a quick shutdown
    def signal_handler(sig, frame):
        print("Signal received, initiating quick shutdown...")
        sys.exit(0)
    
    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Wait for a short time
        print("Press Ctrl+C twice within 5 seconds to trigger the error")
        await asyncio.sleep(5)
        print("No Ctrl+C received, exiting normally")
    finally:
        print("Main task completed")
        # We don't wait for the long_running_task to complete


if __name__ == "__main__":
    asyncio.run(main())