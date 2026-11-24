import os

import grpc
import helloworld2_pb2
import helloworld2_pb2_grpc

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.traces
from sentry_sdk.integrations.grpc import GRPCIntegration
# from sentry_sdk.integrations.grpc.client import ClientInterceptor
# from sentry_sdk.integrations.grpc.aio.client import ClientInterceptor


SERVER_PORT = 8000


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "debug": True,
        "integrations": [GRPCIntegration(), LoggingIntegration(event_level=logging.ERROR, level=None)],
        "data_collection": {"stack_frame_variables": {"mode": "denylist"}},
        "attach_stacktrace": False,
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.traces.start_span(name="grcp_client", attributes={"sentry.op": "function"}):
        print("Will try to greet world ...")

        with grpc.insecure_channel(f"localhost:{SERVER_PORT}") as channel:
            # channel = grpc.intercept_channel(channel, *[ClientInterceptor()])
            stub = helloworld2_pb2_grpc.Greeter2Stub(channel)
            response = stub.SayHello2(helloworld2_pb2.HelloRequest2(name="beautiful world of gRPC"))
            raise TypeError("xyz!")
            print("Greeter client received: " + response.message)

main()
