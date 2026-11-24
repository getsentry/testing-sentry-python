import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),
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

# ExceptionGroup
# OK: this has the same group in 2.x and 3.x
# OLD SDK: https://sentry-sdks.sentry.io/issues/6731520593/events/5d30d9e62865485cae58a9a1dd395772/?project=5461230&query=is%3Aunresolved&referrer=previous-event&stream_index=0
# NEW SDK: https://sentry-sdks.sentry.io/issues/6731520593/events/latest/?project=5461230&query=is%3Aunresolved&referrer=latest-event&stream_index=0
try:
    try:
        raise ExceptionGroup("group", [ValueError("child1"), ValueError("child2")])
    finally:
        raise TypeError("bar")
except BaseException:
    sentry_sdk.capture_exception()


# chained exception
# OK: this has the same group in 2.x and 3.x
# OLD SDK: https://sentry-sdks.sentry.io/issues/6745778412/events/cae2964e7fc7469abacba379a11e202a/?project=5461230&query=is%3Aunresolved&referrer=previous-event&stream_index=1
# NEW SDK: https://sentry-sdks.sentry.io/issues/6745778412/events/548836a7eb24431d91ec2af93b425bba/?project=5461230&query=is%3Aunresolved&referrer=next-event&stream_index=1
try:
    try:
        try:
            raise ValueError("value error")
        finally:
            raise TypeError("type error")
    except BaseException as ex:
        raise NotImplementedError("not implemented error") from ex

except BaseException:
    sentry_sdk.capture_exception()


# Real world example
# OK: this has the same group in 2.x and 3x.
# I also tested with different ordering of the tasks (switched the delay of the first failing_task from 0.1 to 0.11 and back with both SDKs, always the same group!)
# OLD SDK: https://sentry-sdks.sentry.io/issues/6745862253/events/b236e834a92c4952a2dd2758e457a2e8/?project=5461230&query=is%3Aunresolved&referrer=previous-event&stream_index=0
# NEW SDK: https://sentry-sdks.sentry.io/issues/6745862253/events/latest/?project=5461230&query=is%3Aunresolved&referrer=latest-event&stream_index=0
import asyncio


async def failing_task(task_id: int, delay: float, error_type: str):
    await asyncio.sleep(delay)
    if error_type == "impl":
        raise NotImplementedError(f"Error in task {task_id}: not implemented")
    elif error_type == "type":
        raise TypeError(f"Error in task {task_id}: type error")
    return f"Task {task_id} success"


async def run_multiple_tasks():
    # TaskGroup automatically creates ExceptionGroup when multiple tasks fail
    async with asyncio.TaskGroup() as tg:
        tg.create_task(failing_task(1, 0.1, "impl"))
        tg.create_task(failing_task(2, 0.1, "type"))
        tg.create_task(failing_task(3, 0.1, "not_failing"))
        tg.create_task(failing_task(4, 0.1, "impl"))


try:
    asyncio.run(run_multiple_tasks())
except ExceptionGroup:
    sentry_sdk.capture_exception()
