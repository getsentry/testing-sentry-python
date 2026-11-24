import time
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import logger as sentry_logger
from sentry_sdk.consts import VERSION as SENTRY_SDK_VERSION
from sentry_sdk.feature_flags import add_feature_flag
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration


sentry_sdk.init(
    environment=f"lambda-{SENTRY_SDK_VERSION}",
    release=SENTRY_SDK_VERSION,
    dsn="https://d655584d05f14c58b86e9034aab6817f@o447951.ingest.sentry.io/5461230",
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # To collect profiles for all profile sessions,
    # set `profile_session_sample_rate` to 1.0.
    profile_session_sample_rate=1.0,
    # Profiles will be automatically collected while
    # there is an active span.
    profile_lifecycle="trace",
    integrations=[
        AwsLambdaIntegration(),
        LoggingIntegration(event_level=logging.ERROR),
    ],
    debug=True,
    data_collection={"stack_frame_variables": {"mode": "denylist"}},
    attach_stacktrace=False,
)


def _fibonacci(n):
    print(f"fibonacci {n}")
    time.sleep(0.05)

    if n < 0:
        raise ValueError("Incorrect input: n must be non-negative")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return _fibonacci(n-1) + _fibonacci(n-2)



def lambda_handler(event, context):
    user = {
        "id": "testuser",
        "username": "Test User",
    }

    # feature flag
    add_feature_flag("test-flag", True)

    # spans
    with sentry_sdk.start_span(name="test-span-2"):
        # tag
        sentry_sdk.set_tag("test-tag", "test-value")

        # user
        sentry_sdk.set_user(user)

        # breadcrumb
        sentry_sdk.add_breadcrumb(
            category="test-category",
            message="test breadcrumb",
            level="info",
            data={"user": user},
        )

        # context
        sentry_sdk.set_context("test-context", {"text-context-user": user})

        # attachments
        sentry_sdk.add_attachment(bytes=b"Hello Error World", filename="hello-on-error.txt")
        sentry_sdk.add_attachment(bytes=b"Hello Transaction World", filename="hello-on-transaction.txt")

        # logs
        sentry_logger.warning("test log")

        # do some work, so we have a profile
        _fibonacci(5)

        1/0

        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }
