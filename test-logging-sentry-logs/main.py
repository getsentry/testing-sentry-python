import asyncio
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import logger as sentry_logger

import logging
logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        integrations=[
            LoggingIntegration(
                breadcrumb_level=logging.DEBUG,
                event_level=logging.ERROR,
                level=logging.WARNING,
            ),
        ],
        traces_sample_rate=1.0,
        debug=True,
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    my_value = "SomeStringValue"

    with sentry_sdk.start_span(name="logging-transaction", attributes={"sentry.op": "function"}):
        sentry_logger.debug("Calling API directly. Thats the status: {my_status} / and the value: {my_value}", my_status=200, my_value="some value")

        logger.critical("Using integration and setting stack_info, stacklevel, and extra[my_status, my_value]. %s", my_value, stack_info=True, stacklevel=2, extra={"my_status": 200, "my_value": "some value"})

        logger.debug("Using python.logging.debug, my_value: %s", my_value)
        logger.info("Using python.logging.info, my_value: %s", my_value)
        logger.warning("Using python.logging.warning, my_value: %s", my_value)
        logger.error("Using python.logging.error, my_value: %s", my_value)
        logger.critical("Using python.logging.critical, my_value: %s", my_value)
        logger.exception("Using python.logging.exception, my_value: %s", my_value)

        logger.debug(f"[f-string version] Using python.logging.debug, my_value: {my_value}")
        logger.info(f"[f-string version] Using python.logging.info, my_value: {my_value}")
        logger.warning(f"[f-string version] Using python.logging.warning, my_value: {my_value}")
        logger.error(f"[f-string version] Using python.logging.error, my_value: {my_value}")
        logger.critical(f"[f-string version] Using python.logging.critical, my_value: {my_value}")
        logger.exception(f"[f-string version] Using python.logging.exception, my_value: {my_value}")


if __name__ == "__main__":
    asyncio.run(main())
