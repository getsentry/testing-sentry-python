import os

import sentry_sdk
from sentry_sdk.integrations.clickhouse_driver import ClickhouseDriverIntegration

from clickhouse_driver import Client

def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "trace_lifecycle": "stream",
        "send_default_pii": True,
        "debug": True,
        "integrations": [ClickhouseDriverIntegration()],
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.start_transaction(op="function", name="clickhouse_driver"):
        client = Client(host='localhost', )
        client.execute("DROP TABLE IF EXISTS test")
        client.execute("CREATE TABLE test (x Int32) ENGINE = Memory")
        client.execute("INSERT INTO test (x) VALUES", [{"x": 100}])
        client.execute("INSERT INTO test (x) VALUES", [[170], [200]])

        res = client.execute("SELECT sum(x) FROM test WHERE x > %(minv)i", {"minv": 150})
        print(res)


main()