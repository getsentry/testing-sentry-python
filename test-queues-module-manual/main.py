import os
import time

from datetime import datetime, timezone

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def main():
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
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

    # The message you want to send to the queue
    queue = "messages"
    message = "Hello World!"
    message_id = "abc123"

    ### PUBLISH

    # Create the span
    with sentry_sdk.start_span(name="queue_producer_transaction", attributes={"sentry.op": "function"}) as transaction:
        with sentry_sdk.start_span(name="queue_producer", attributes={"sentry.op": "queue.publish"}) as span:    
            # Set span data
            span.set_attribute("messaging.message.id", message_id)
            span.set_attribute("messaging.destination.name", queue)
            span.set_attribute("messaging.message.body.size", len(message.encode("utf-8")))
            
            ts = int(datetime.now(timezone.utc).timestamp())

            headers = {
                "sentry-trace": sentry_sdk.get_traceparent(),
                "baggage": sentry_sdk.get_baggage()            
            }
        

            # Publish the message to the queue (including trace information and current time stamp)
            # connection.publish(
            #     queue=queue,
            #     body=message,
            #     timestamp=now,
            #     headers = {
            #         "sentry-trace": sentry_sdk.get_traceparent()
            #         "baggage": sentry_sdk.get_baggage()            
            #     },
            # )


    time.sleep(0.3)


    ### CONSUME
    message = {
        "message_id": "abc123",
        "body": "Hello World!",
        "timestamp": ts,
        "headers": headers,
    }

    # Calculate latency (optional, but valuable)
    now = datetime.now(timezone.utc)
    message_time = datetime.fromtimestamp(message["timestamp"], timezone.utc)
    latency =  now - message_time

    # Continue the trace started in the producer
    sentry_sdk.continue_trace(message["headers"])
    with sentry_sdk.start_span(name="queue_consumer_transaction", attributes={"sentry.op": "function"}):
        # Create the span
        with sentry_sdk.start_span(name="queue_consumer", attributes={"sentry.op": "queue.process"}) as span:
            # Set span data
            span.set_attribute("messaging.message.id", message["message_id"])
            span.set_attribute("messaging.destination.name", queue)
            span.set_attribute("messaging.message.body.size", message["body"])
            span.set_attribute("messaging.message.receive.latency", latency.total_seconds()*1000)
            span.set_attribute("messaging.message.retry.count", 0)
            
            try:
                # Process the message
                # process_message(message)
                pass
            except Exception:
                span.status = "error"            


if __name__ == "__main__":
    main()
