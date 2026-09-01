import os

import sentry_sdk



def main():
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=1.0,
        trace_lifecycle="stream",
        debug=True,
    )

    client = sentry_sdk.Client(
        dsn="http://123@localhost:9999/0",
    )

    scope = sentry_sdk.get_current_scope().fork()
    scope.set_client(client)

    event = {
        "message": "Hello, world!",
        "level": "error",
    }

    with sentry_sdk.use_scope(scope):
        event_id = scope.capture_event(event)
        print(event_id)

    # for i in range(100):
    #     try:
    #         division_by_zero = 1 / 0
    #     except Exception as e:
    #         sentry_sdk.capture_exception(e)


if __name__ == "__main__":
    main()
