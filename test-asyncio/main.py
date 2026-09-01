import asyncio
import os
import random

import sentry_sdk
import sentry_sdk.traces
from sentry_sdk.integrations.asyncio import AsyncioIntegration


# The dynamic sampling context is deliberately not recorded. Sampling is
# configured through traces_sample_rate / traces_sampler, and copying DSC
# internals onto a span as attributes would misrepresent them as span data.
TRACE_CONTEXT_SKIP_KEYS = {"dynamic_sampling_context"}


def flatten_trace_context(prefix, context):
    """Flatten a trace context dict into scalar span attributes.

    Streamed spans have no concept of context, so values that used to be set
    via `set_context()` become attributes instead. Keys are prefixed so the
    current and isolation scopes do not overwrite each other's identically
    named entries. `None` values are skipped -- they would otherwise serialize
    as the string "None".
    """
    return {
        f"{prefix}.{key}": value
        for key, value in (context or {}).items()
        if value is not None and key not in TRACE_CONTEXT_SKIP_KEYS
    }


def set_span_attributes(span):
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
        set_span_attributes(span)
        print(f"Consume {name} starting")
        await asyncio.sleep(0.4)
        print(f"Consume {name} completed")


async def task_kafka_producer(name):
    with sentry_sdk.traces.start_span(name=f"Produce {name}") as span:
        set_span_attributes(span)

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
        set_span_attributes(span)

        # Create some tasks
        tasks = []
        for i in range(5):
            tasks.append(asyncio.create_task(task_kafka_producer(f"Task-{i+1}")))

        # Execute the tasks concurrently
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
