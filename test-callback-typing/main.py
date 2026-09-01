import asyncio
import os

import sentry_sdk
import sentry_sdk.traces
from sentry_sdk.types import Event, Hint, SamplingContext, Breadcrumb, BreadcrumbHint, MonitorConfig, SpanJSON
from sentry_sdk.crons import MonitorStatus, capture_checkin


def my_error_sampler(event: Event, hint: Hint) -> float | bool:
    return True


def my_traces_sampler(sampling_context: SamplingContext) -> float | bool:
    return 1.0


def my_profiles_sampler(sampling_context: SamplingContext) -> float | bool:
    return True


def my_before_send(event: Event, hint: Hint) -> Event | None:
    return event


def my_before_send_span(span: SpanJSON, hint: Hint) -> SpanJSON:
    return span


def my_before_breadcrumb(crumb: Breadcrumb, hint: BreadcrumbHint) -> Breadcrumb | None:
    return crumb




async def main() -> None:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        trace_lifecycle="stream",
        profiles_sample_rate=1.0,
        send_default_pii=True,
        debug=True,
        error_sampler=my_error_sampler,
        traces_sampler=my_traces_sampler,
        profiles_sampler=my_profiles_sampler,
        before_send=my_before_send,
        before_send_span=my_before_send_span,
        before_breadcrumb=my_before_breadcrumb,
    )

    my_config: MonitorConfig = {}

    capture_checkin()


    with sentry_sdk.traces.start_span(name="test-span"):
        try:
            1 / 0
        except Exception:
            sentry_sdk.capture_exception()


if __name__ == "__main__":
    asyncio.run(main())
