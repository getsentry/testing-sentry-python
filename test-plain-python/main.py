import os

import sentry_sdk


def main():
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=1.0,
        trace_lifecycle="stream",
        debug=True,
    )

    for i in range(10):
        try:
            division_by_zero = 1 / 0
        except Exception as e:
            sentry_sdk.capture_exception(e)


if __name__ == "__main__":
    main()
