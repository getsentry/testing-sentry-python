import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.traces
from sentry_sdk.integrations.clickhouse_driver import ClickhouseDriverIntegration

from clickhouse_driver import Client

def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "debug": True,
        "integrations": [ClickhouseDriverIntegration(), LoggingIntegration(event_level=logging.ERROR, level=None)],
        "data_collection": {"stack_frame_variables": {"mode": "denylist"}},
        "attach_stacktrace": False,
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.traces.start_span(name="clickhouse_driver", attributes={"sentry.op": "function"}):
        client = Client(host='localhost', )
        client.execute("DROP TABLE IF EXISTS test")
        client.execute("CREATE TABLE test (x Int32) ENGINE = Memory")
        client.execute("INSERT INTO test (x) VALUES", [{"x": 100}])
        client.execute("INSERT INTO test (x) VALUES", [[170], [200]])

        res = client.execute("SELECT sum(x) FROM test WHERE x > %(minv)i", {"minv": 150})
        print(res)


main()