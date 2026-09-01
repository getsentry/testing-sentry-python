import asyncio
import os
import random

import sentry_sdk
import sentry_sdk.traces
from sentry_sdk.integrations.asyncio import AsyncioIntegration


def set_trace_context_attributes(span, prefix, context):
    """Record a trace context on a streamed span as attributes.

    Streamed spans have no concept of context, so values that used to be set
    via `set_context()` are set as attributes instead. Attributes hold scalars
    (or lists of scalars), so nested dicts such as `dynamic_sampling_context`
    are flattened with dotted keys. Passing a dict straight to
    `set_attribute()` does not raise -- it stringifies it with `repr()` into an
    unparseable blob -- so flatten explicitly.
    """
    for key, value in (context or {}).items():
        if value is None:
            continue
        if isinstance(value, dict):
            set_trace_context_attributes(span, f"{prefix}.{key}", value)
        else:
            span.set_attribute(f"{prefix}.{key}", value)


def set_scope_trace_contexts(span):
    set_trace_context_attributes(
        span,
        "current-scope-trace-context",
        sentry_sdk.get_current_scope().get_trace_context() or {"empty": True},
    )
    set_trace_context_attributes(
        span,
        "isolation-scope-trace-context",
        sentry_sdk.get_isolation_scope().get_trace_context(),
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
