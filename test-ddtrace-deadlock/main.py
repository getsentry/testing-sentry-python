import os
import wrapt
import logging

logging.basicConfig(level=logging.INFO)

class _BadLock(wrapt.ObjectProxy):

    def __init__(self, wrapped):
        wrapt.ObjectProxy.__init__(self, wrapped)

    def release(self, *args, **kwargs):
        logging.info('releasing 11')
        return self.__wrapped__.release(*args, **kwargs)

import threading

OriginalLock = threading.Lock

def create_bad_lock(*args, **kwargs):
    lock = OriginalLock(*args, **kwargs)
    return _BadLock(lock)

threading.Lock = create_bad_lock


import sentry_sdk
import logging
import threading
import time
import traceback

from sentry_sdk.integrations.logging import LoggingIntegration
import sys


def get_stacktrace() -> str:
    """Returns the stacktrace as a string. Don't call this all the time because it's expensive."""
    code = []
    current_thread_id = threading.get_ident()

    frames = list(sys._current_frames().items())
    # Move current thread to the end
    current_thread_id_idx = None
    for i, (thread_id, _stack) in enumerate(frames):
        if thread_id == current_thread_id:
            current_thread_id_idx = i
            break

    if current_thread_id_idx is not None:
        frames.append(frames.pop(current_thread_id_idx))

    for thread_id, stack in frames:
        prefix = 'Current thread' if thread_id == current_thread_id else 'Thread'

        code.append(f'{prefix} {hex(thread_id)} (most recent call first):')
        for filename, lineno, name, line in reversed(traceback.extract_stack(stack)):
            if name == 'print_stacks_signal_handler':
                continue
            code.append('  File "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append(f'    {line.strip()}')

        code[-1] += '\n'

    return '\n'.join(code)


def print_out_threads():
    time.sleep(10)

    for th in threading.enumerate():
        print("~~~~~~~~~~")
        print(th)
        traceback.print_stack(sys._current_frames()[th.ident])
        print()    

    # print(get_stacktrace())

thread = threading.Thread(target=print_out_threads, daemon=True)
thread.start()


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment='local',
    integrations=[
        LoggingIntegration(
            breadcrumb_level=logging.INFO,
            event_level=logging.INFO,
            level=None,  #WARNING,
        ),
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


logging.info('test 11')