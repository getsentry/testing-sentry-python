import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def main():
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        # enable_tracing=True,
        traces_sample_rate=1.0,
        environment="test-plain-python-data-attributes",
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

    with sentry_sdk.start_span(name="xxx-test-transaction") as trx:
        with sentry_sdk.start_span(name="xxx-test-span") as span:
            # sentry_sdk.set_measurement("xxx.global.measurement.value", 1.0)

            trx.set_attribute("xxx.trx.data", "xxx.trx.data.value")
            # trx.set_measurement("xxx.trx.measurement.value", 1.0)
            # trx.set_attribute("xxx.trx.attribute", "xxx.trx.attribute.value")

            span.set_attribute("xxx.span.data", "xxx.span.data.value")
            # span.set_measurement("xxx.span.measurement.value", 1.0)
            # span.set_attribute("xxx.span.attribute", "xxx.span.attribute.value")

            division_by_zero = 1 / 0


if __name__ == "__main__":
    main()
