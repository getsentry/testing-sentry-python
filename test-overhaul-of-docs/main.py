import os
# import asyncio
# import httpx
import pymongo

import sentry_sdk
# from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
# from sentry_sdk.integrations.asyncio import AsyncioIntegration
# from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.pymongo import PyMongoIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

# async def main():
#     sentry_settings = {
#         "dsn": os.getenv("SENTRY_DSN", None),
#         "environment": os.getenv("ENV", "local"),
#         "traces_sample_rate": 1.0,
#         "send_default_pii": True,
#         "debug": True,
#         "integrations": [AsyncioIntegration()],
#     }
#     print(f"Sentry Settings: {sentry_settings}")

#     sentry_sdk.init(**sentry_settings)

#     asyncio.create_task(my_task())

# asyncio.run(main())

# import redis

# def main():
#     sentry_settings = {
#         "dsn": os.getenv("SENTRY_DSN", None),
#         "environment": os.getenv("ENV", "local"),
#         "traces_sample_rate": 1.0,
#         # "send_default_pii": True,
#         "debug": True,
#         "integrations": [PyMongoIntegration()],
#     }
#     print(f"Sentry Settings: {sentry_settings}")

#     sentry_sdk.init(**sentry_settings)


#     DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
#     DATABASE_PORT = 27017

#     client = pymongo.MongoClient(DATABASE_HOST, DATABASE_PORT)


#     with sentry_sdk.start_transaction(name="testing_sentry"):
#         r = redis.Redis(host='localhost', port=6379, decode_responses=True)
#         r.set("foo", "bar")
#         r.get("foo")

# main()



# import asyncio
# import redis.asyncio as redis

# async def main():
#     sentry_settings = {
#         "dsn": os.getenv("SENTRY_DSN", None),
#         "environment": os.getenv("ENV", "local"),
#         "traces_sample_rate": 1.0,
#         # "send_default_pii": True,
#         "debug": True,
#         "integrations": [PyMongoIntegration()],
#     }
#     print(f"Sentry Settings: {sentry_settings}")

#     sentry_sdk.init(**sentry_settings)

#     r = redis.Redis()
    
#     with sentry_sdk.start_transaction(name="testing_sentry"):    
#         await r.set("async_foo", "bar")
#         await r.get("async_foo")
        
# asyncio.run(main())


# from sqlalchemy import create_engine
# from sqlalchemy.sql import text

# def main():
#     sentry_settings = {
#         "dsn": os.getenv("SENTRY_DSN", None),
#         "environment": os.getenv("ENV", "local"),
#         "traces_sample_rate": 1.0,
#         # "send_default_pii": True,
#         "debug": True,
#         "integrations": [PyMongoIntegration()],
#     }
#     print(f"Sentry Settings: {sentry_settings}")

#     sentry_sdk.init(**sentry_settings)

#     DATABASE_URL = 'postgresql://demo_app_django_react:demo_app_django_react@localhost:5433/demo_app_django_react'

#     engine = create_engine(DATABASE_URL, echo=True)
#     statement = text("SELECT 'Hello World'")

#     with engine.connect() as conn:
#         with sentry_sdk.start_transaction(name="testing_sentry"):
#             result = conn.execute(statement)

# main()




# import asyncio
# import aiohttp

# async def main():
#     sentry_settings = {
#         "dsn": os.getenv("SENTRY_DSN", None),
#         "environment": os.getenv("ENV", "local"),
#         "traces_sample_rate": 1.0,
#         # "send_default_pii": True,
#         "debug": True,
#         "integrations": [AioHttpIntegration()],
#     }
#     print(f"Sentry Settings: {sentry_settings}")

#     sentry_sdk.init(**sentry_settings)

#     with sentry_sdk.start_transaction(name="testing_sentry"):
#         async with aiohttp.ClientSession() as session:
#             async with session.get("https://sentry.io/") as response:
#                 print("Status:", response.status)    
#             async with session.post("http://httpbin.org/post") as response:
#                 print("Status:", response.status)    
                
# asyncio.run(main())

# import sentry_sdk

# from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# def app(env, start_response):
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     response_body = 'Hello World'
#     1/0
#     return [response_body.encode()]

# app = SentryWsgiMiddleware(app)

# # Run the application in a mini WSGI server.
# from wsgiref.simple_server import make_server
# make_server('', 8000, app).serve_forever()


# from bottle import Bottle, run

# import sentry_sdk
# from sentry_sdk.integrations.bottle import BottleIntegration

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [BottleIntegration()],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# app = Bottle()

# @app.route('/')
# def hello():
#     1/0
#     return "Hello World!"

# run(app, host='localhost', port=8080)


# import falcon

# from sentry_sdk.integrations.falcon import FalconIntegration

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [FalconIntegration()],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)


# class HelloWorldResource:
#     def on_get(self, req, resp):
#         message = {
#             'hello': "world",
#         }
#         1 / 0  # raises an error
#         resp.media = message

# app = falcon.App()
# app.add_route('/', HelloWorldResource())



# from quart import Quart

# import sentry_sdk
# from sentry_sdk.integrations.quart import QuartIntegration

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [QuartIntegration()],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# app = Quart(__name__)

# @app.route("/")
# async def hello():
#     1/0  # raises an error
#     return {"hello": "world"}

# app.run()






# from sanic import Sanic
# from sanic.response import text

# import sentry_sdk
# from sentry_sdk.integrations.quart import QuartIntegration

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [QuartIntegration()],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# app = Sanic("MyHelloWorldApp")

# @app.get("/")
# async def hello_world(request):
#     1 / 0  # raises an error
#     return text("Hello, world.")





# from aiohttp import web


# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     # "integrations": [],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# async def hello(request):
#     1/0  # raises an error
#     return web.Response(text="Hello, world")

# app = web.Application()
# app.add_routes([web.get('/', hello)])

# web.run_app(app)



# from wsgiref.simple_server import make_server
# from pyramid.config import Configurator
# from pyramid.response import Response

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# def hello_world(request):
#     1/0  # raises an error
#     return Response('Hello World!')

# if __name__ == '__main__':
#     with Configurator() as config:
#         config.add_route('hello', '/')
#         config.add_view(hello_world, route_name='hello')
#         app = config.make_wsgi_app()

#     server = make_server('0.0.0.0', 6543, app)
#     server.serve_forever()






# import asyncio
# import tornado

# import sentry_sdk
# from sentry_sdk.integrations.tornado import TornadoIntegration

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [TornadoIntegration()],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         1/0  # raises an error
#         self.write("Hello, world")

# def make_app():
#     return tornado.web.Application([
#         (r"/", MainHandler),
#     ])

# async def main():
#     app = make_app()
#     app.listen(8888)
#     await asyncio.Event().wait()

# asyncio.run(main())    

# # main.py
# from redis import Redis
# from rq import Queue

# from jobs import hello 

# import sentry_sdk

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# q = Queue(connection=Redis())
# with sentry_sdk.start_transaction(name="testing_sentry"):
#     result = q.enqueue(hello, "World")





# from sentry_sdk.integrations.socket import SocketIntegration

# import socket 

# def main():
#     sentry_settings = {
#         "dsn": os.getenv("SENTRY_DSN", None),
#         "environment": os.getenv("ENV", "local"),
#         "traces_sample_rate": 1.0,
#         # "send_default_pii": True,
#         "debug": True,
#         "integrations": [SocketIntegration()],
#     }
#     print(f"Sentry Settings: {sentry_settings}")
#     sentry_sdk.init(**sentry_settings)

#     with sentry_sdk.start_transaction(name="testing_sentry"):
#         timeout = 10
#         socket.getaddrinfo("sentry.io", 443)
#         socket.create_connection(("sentry.io", 443), timeout, None)
# main()






# from flask import Flask

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     1/0  # raises an error
#     return "<p>Hello, World!</p>"



# from sentry_sdk.integrations.pure_eval import PureEvalIntegration

# sentry_settings = {
#     "dsn": os.getenv("SENTRY_DSN", None),
#     "environment": os.getenv("ENV", "local"),
#     "traces_sample_rate": 1.0,
#     # "send_default_pii": True,
#     "debug": True,
#     "integrations": [PureEvalIntegration()],
# }
# print(f"Sentry Settings: {sentry_settings}")
# sentry_sdk.init(**sentry_settings)

# from types import SimpleNamespace

# def main():
#     namespace = SimpleNamespace()
#     namespace.d = {1: 2}
#     print(namespace.d[1] / 0)

# main()


def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        # "send_default_pii": True,
        "debug": True,
        "trace_lifecycle": "stream",
        "integrations": [],
    }
    print(f"Sentry Settings: {sentry_settings}")
    sentry_sdk.init(**sentry_settings)

    # This will create bytecode that starts a finally statement that is never ended, thus crashing the Python interpreter.
    exec(type((lambda: 0).__code__)(0, 0, 0, 0, 0, 0, b'\x053', (), (), (), '', '', 0, b''))

main()