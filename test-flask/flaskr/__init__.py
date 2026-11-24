
import os

from flask import Flask
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sqlalchemy
from sqlalchemy.sql import text


def create_app(test_config=None):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment='development',
        release='unknown',
        traces_sample_rate=1.0,
        enable_db_query_source=True,
        db_query_source_threshold_ms=0,
        debug=True,
        integrations=[LoggingIntegration(event_level=logging.ERROR, level=None)],
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

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/err')
    def err():
        1/0

    @app.route('/db-err')
    def db_err():
        engine = sqlalchemy.create_engine(f'sqlite:///instance/flaskr.sqlite')
        with engine.connect() as con:
            statement = text('SELECT * FROM user')
            result = con.execute(statement)
        1/0

    from . import db
    db.init_app(app)

    return app
