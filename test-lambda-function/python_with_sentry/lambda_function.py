import json
import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        AwsLambdaIntegration(
            timeout_warning=True,
        ),
        LoggingIntegration(event_level=logging.ERROR, level=None),
    ],
    traces_sample_rate=1.0,
    debug=True,
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

def lambda_handler(event, context):
    # TODO implement
    1/0
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
