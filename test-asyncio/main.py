import asyncio
import os
import random

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration


async def task_kafka_consumer(name):
    with sentry_sdk.start_transaction(name=f"Consume {name}") as trx:
        trx.set_context("current-scope-trace-context", sentry_sdk.get_current_scope().get_trace_context() or {"empty": True})
        trx.set_context("isolation-scope-trace-context", sentry_sdk.get_isolation_scope().get_trace_context())
        print(f"Consume {name} starting")
        await asyncio.sleep(0.4)
        print(f"Consume {name} completed")


async def task_kafka_producer(name):
    with sentry_sdk.start_transaction(name=f"Produce {name}") as trx:
        trx.set_context("current-scope-trace-context", sentry_sdk.get_current_scope().get_trace_context() or {"empty": True})
        trx.set_context("isolation-scope-trace-context", sentry_sdk.get_isolation_scope().get_trace_context())

        print(f"Producer {name} starting")
        await asyncio.sleep(0.01)
        await asyncio.create_task(task_kafka_consumer(name))
        print(f"Producer {name} completed")


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        trace_lifecycle="stream",
        debug=True,
        integrations=[
            AsyncioIntegration(),  # IMPORTANT: We need to enable this by hand!
        ], 
    )

    with sentry_sdk.start_transaction(name="main (created by FastAPI)") as trx:
        trx.set_context("current-scope-trace-context", sentry_sdk.get_current_scope().get_trace_context() or {"empty": True})
        trx.set_context("isolation-scope-trace-context", sentry_sdk.get_isolation_scope().get_trace_context())

        # Create some tasks
        tasks = []
        for i in range(5):
            tasks.append(asyncio.create_task(task_kafka_producer(f"Task-{i+1}")))

        # Execute the tasks concurrently
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
