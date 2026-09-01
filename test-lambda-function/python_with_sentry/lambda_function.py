import json
import os

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        AwsLambdaIntegration(
            timeout_warning=True,
        ),
    ],
    traces_sample_rate=1.0,
    trace_lifecycle="stream",
    debug=True,
)

def lambda_handler(event, context):
    # TODO implement
    1/0
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
