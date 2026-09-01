import asyncio
import os
from concurrent import futures

import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import sentry_sdk
from sentry_sdk.integrations.grpc.server import ServerInterceptor
from sentry_sdk.integrations.grpc import GRPCIntegration


SERVER_PORT = 8000


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    async def SayHello(self, request, context):
        1/0
        return helloworld_pb2.HelloReply(message="X Hello, %s!" % request.name)


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

    server = grpc.aio.server(
        # thread_pool = futures.ThreadPoolExecutor(max_workers=10), 
        # interceptors=[ServerInterceptor()],
    )
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"[::]:{SERVER_PORT}")
    print(f"Server started, listening on {SERVER_PORT}")
    await server.start()
    await server.wait_for_termination()         


asyncio.run(main())