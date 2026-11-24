import os

from fastapi import FastAPI
import ldclient
from ldclient.config import Config
from ldclient.context import Context

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import logger as sentry_logger
from sentry_sdk.feature_flags import add_feature_flag
from sentry_sdk.consts import VERSION as SENTRY_SDK_VERSION
from sentry_sdk.integrations.launchdarkly import LaunchDarklyIntegration

DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# Initialize LaunchDarkly client
ldclient.set_config(Config(os.environ.get("LAUNCHDARKLY_SDK_KEY")))
ld_client = ldclient.get()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=f"{DIR}-{SENTRY_SDK_VERSION}",
    release=SENTRY_SDK_VERSION,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    debug=True,
    integrations=[
        LaunchDarklyIntegration(),
        LoggingIntegration(event_level=logging.ERROR),
    ],
    spotlight="http://localhost:9999/api/0/envelope/",
    data_collection={"stack_frame_variables": {"mode": "denylist"}},
    attach_stacktrace=False,
)


app = FastAPI()


@app.get("/error")
async def error():
    user = {
        "id": "testuser",
        "username": "Test User",
    }

    # feature flag
    add_feature_flag("test-flag-1", True)
    add_feature_flag("test-flag-2", True)
    add_feature_flag("test-flag-3", True)
    add_feature_flag("test-flag-4", True)
    add_feature_flag("test-flag-5", True)
    add_feature_flag("test-flag-6", True)
    add_feature_flag("test-flag-7", True)
    add_feature_flag("test-flag-8", True)
    add_feature_flag("test-flag-9", True)
    add_feature_flag("test-flag-10", True)

    # spans
    with sentry_sdk.start_span(name="test-span"):
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

            # attachments (2.x)
            # scope = sentry_sdk.get_current_scope()
            # scope.add_attachment(bytes=b"Hello Error World", filename="hello-on-error.txt")
            # scope.add_attachment(bytes=b"Hello Transaction World", filename="hello-on-transaction.txt", add_to_transactions=True)

            # attachments (3.x)
            sentry_sdk.add_attachment(bytes=b"Hello Error World", filename="hello-on-error.txt")
            sentry_sdk.add_attachment(bytes=b"Hello Transaction World", filename="hello-on-transaction.txt")

            # logs
            sentry_logger.warning("test log")

            # Evaluate LaunchDarkly flag
            context = Context.builder("context-key-123abc").set("id", user["id"]).set("username", user["username"]).build()
            should_raise_error = ld_client.variation("raise-error-flag", context, True)

            if should_raise_error:
                add_feature_flag("span-flag-1", True)
                ld_client.variation("span-flag-2", Context.create("my-org", "organization"), False)
                raise ValueError("help! an error!")


@app.get("/")
async def index():
    return {
        "hello": "world!",
        "errors-are-here": "http://localhost:5000/error",
    }
