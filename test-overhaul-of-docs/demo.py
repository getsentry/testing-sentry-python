import os 

import sentry_sdk
from sentry_sdk.integrations.arq import ArqIntegration

sentry_settings = {
    "dsn": os.getenv("SENTRY_DSN", None),
    "environment": os.getenv("ENV", "local"),
    "traces_sample_rate": 1.0,
    # "send_default_pii": True,
    "debug": True,
    "trace_lifecycle": "stream",
    "integrations": [ArqIntegration()],
}
print(f"Sentry Settings: {sentry_settings}")

sentry_sdk.init(**sentry_settings)

async def add_numbers(ctx, a, b):
    1/0
    return a + b

class WorkerSettings:
    functions = [add_numbers]