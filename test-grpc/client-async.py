import asyncio
import os

import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import sentry_sdk
from sentry_sdk.integrations.grpc import GRPCIntegration
# from sentry_sdk.integrations.grpc.client import ClientInterceptor
from sentry_sdk.integrations.grpc.aio.client import ClientInterceptor


SERVER_PORT = 8000


async def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "trace_lifecycle": "stream",
        "send_default_pii": True,
        "debug": True,
        "integrations": [GRPCIntegration()],
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.start_transaction(op="function", name="grcp_client"):
        print("Will try to greet world ...")

        async with grpc.aio.insecure_channel(f"localhost:{SERVER_PORT}") as channel:
            # channel = grpc.intercept_channel(channel, *[ClientInterceptor()])
            stub = helloworld_pb2_grpc.GreeterStub(channel)
            response = await stub.SayHello(helloworld_pb2.HelloRequest(name="beautiful world of gRPC"))

            print("Greeter client received: " + response.message)


asyncio.run(main())
