import asyncio
import os
import random

import sentry_sdk
import sentry_sdk.traces
from sentry_sdk.integrations.asyncio import AsyncioIntegration


def flatten_trace_context(prefix, context):
    """Flatten a trace context dict into scalar span attributes.

    Streamed spans have no concept of context, so values that used to be set
    via `set_context()` become attributes. Two wrinkles force the flattening:
    `get_trace_context()` nests a `dynamic_sampling_context` dict, and
    `set_attribute()` coerces a dict with `repr()` rather than rejecting it,
    which would yield an unparseable blob. Prefixing also keeps the current
    and isolation scopes from overwriting each other's identically named keys.
    """
    flat = {}
    for key, value in (context or {}).items():
        if value is None:
            # Would otherwise serialize as the string "None".
            continue
        if isinstance(value, dict):
            flat.update(flatten_trace_context(f"{prefix}.{key}", value))
        else:
            flat[f"{prefix}.{key}"] = value
    return flat


def set_scope_trace_contexts(span):
    span.set_attributes(
        {
            **flatten_trace_context(
                "current-scope-trace-context",
                sentry_sdk.get_current_scope().get_trace_context() or {"empty": True},
            ),
            **flatten_trace_context(
                "isolation-scope-trace-context",
                sentry_sdk.get_isolation_scope().get_trace_context(),
            ),
        }
    )


async def task_kafka_consumer(name):
    with sentry_sdk.traces.start_span(name=f"Consume {name}") as span:
        set_scope_trace_contexts(span)
        print(f"Consume {name} starting")
        await asyncio.sleep(0.4)
        print(f"Consume {name} completed")


async def task_kafka_producer(name):
    with sentry_sdk.traces.start_span(name=f"Produce {name}") as span:
        set_scope_trace_contexts(span)

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

    with sentry_sdk.traces.start_span(name="main (created by FastAPI)") as span:
        set_scope_trace_contexts(span)

        # Create some tasks
        tasks = []
        for i in range(5):
            tasks.append(asyncio.create_task(task_kafka_producer(f"Task-{i+1}")))

        # Execute the tasks concurrently
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
