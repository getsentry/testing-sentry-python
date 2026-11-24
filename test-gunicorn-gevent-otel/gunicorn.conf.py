import logging
import os

bind = "0.0.0.0:8080"
wsgi_app = "main"

worker_class = "gevent"
workers = 1
worker_connections = 1000
max_requests = 25
preload_app = False

reload = True
loglevel = "debug"
errorlog = "-"
accesslog = "-"


def post_fork(server, worker):
    print(f"*** post_fork {server} / {worker}")
    # If Sentry SDK is initialized here, I get the "Monkey-patching ssl after ssl has already been imported may lead to errors" error during the worker init


def post_worker_init(worker):
    print(f"*** post_worker_init {worker}")

    # Initialize OpenTelemetry
    from opentelemetry import trace

    # from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter # NOT using GRPC (because it does not work well with gevent)
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # but HTTP instead

    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({SERVICE_NAME: "myapp", "worker": worker.pid})
    tracer_provider = TracerProvider(resource=resource)

    otlp_endpoint = "127.0.0.1:999"  # non existing endpoint
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    # Initialize Sentry SDK
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.otlp import OTLPIntegration

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        debug=True,
        integrations=[
            OTLPIntegration(setup_propagator=True),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        data_collection={
            "user_info": False,
            "http_bodies": ["incoming_request"],
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
