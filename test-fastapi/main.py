from fastapi import FastAPI, Depends, HTTPException
import os

import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

failed_request_status_codes = [range(400, 600)]
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    trace_lifecycle="stream",
    profiles_sample_rate=1.0,
    debug=True,
    integrations=[
        StarletteIntegration(failed_request_status_codes=failed_request_status_codes),
        FastApiIntegration(failed_request_status_codes=failed_request_status_codes),
    ],
)


app = FastAPI()


def get_user():
    user = {
      "id": "testuser"
    }
    sentry_sdk.set_user(user)
    return user


@app.middleware("http")
async def test_middleware(request, call_next):
    print("middleware")
    return await call_next(request)


@app.get("/error")
def endpoint(user = Depends(get_user)):
    raise ValueError("help! an error!")


@app.post("/post")
def main(user):
    return user


@app.get("/")
def endpoint():
    return {
        "hello": "world!",
        "errors-are-here": "http://localhost:5000/error",
        "http-exception": "http://localhost:5000/http-exception",
    }
