from concurrent import futures
import os

import grpc
import helloworld2_pb2
import helloworld2_pb2_grpc

import sentry_sdk
from sentry_sdk.integrations.grpc import GRPCIntegration
# from sentry_sdk.integrations.grpc.server import ServerInterceptor


SERVER_PORT = 8000


class Greeter(helloworld2_pb2_grpc.Greeter2Servicer):
    def SayHello2(self, request, context):
        # raise TypeError("abc!")
        return helloworld2_pb2.HelloReply2(message="X Hello, %s!" % request.name)


def main():
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

    server = grpc.server(
        thread_pool = futures.ThreadPoolExecutor(max_workers=10), 
        # interceptors=[ServerInterceptor()],
    )
    helloworld2_pb2_grpc.add_Greeter2Servicer_to_server(Greeter(), server)
    server.add_insecure_port(f"[::]:{SERVER_PORT}")
    server.start()
    print(f"Server started, listening on {SERVER_PORT}")
    server.wait_for_termination()         


main()