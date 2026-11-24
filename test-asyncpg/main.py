import asyncio
import asyncpg
import datetime

import os

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk.traces
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration

DATABASE_USER = "demo_app_django_react"
DATABASE_PASSWORD = "demo_app_django_react"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5433"
DATABASE_NAME = "demo_app_django_react"

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"




async def main():
    sentry_settings = {
        "dsn": os.getenv("SENTRY_DSN", None),
        "environment": os.getenv("ENV", "local"),
        "traces_sample_rate": 1.0,
        "debug": True,
        "integrations": [AsyncPGIntegration(), LoggingIntegration(event_level=logging.ERROR, level=None)],
        # "_experiments": {"record_sql_params": True},
        "data_collection": {"stack_frame_variables": {"mode": "denylist"}},
        "attach_stacktrace": False,
    }
    print(f"Sentry Settings: {sentry_settings}")

    sentry_sdk.init(**sentry_settings)

    with sentry_sdk.traces.start_span(
        name="asyncpg", attributes={"sentry.op": "function"}
    ):
        # Establish a connection to an existing database
        conn = await asyncpg.connect(DATABASE_URL)

        rows = await conn.fetch('''
            SELECT * from show_show order by countries, release_year DESC;
        ''')
        
        rows = await conn.fetch('''
            SELECT * from show_show where countries='United States' and release_year=2020;
        ''')

        rows = await conn.fetch('''
            SELECT * from show_show where countries=$1 and release_year=$2;
        ''', "", 2012)

        # # Insert a record into the created table.
        # await conn.execute('''
        #     INSERT INTO users(name, dob) VALUES($1, $2)
        # ''', 'Bob', datetime.date(1984, 3, 1))

        # # Select a row from the table.
        # row = await conn.fetchrow(
        #     'SELECT * FROM users WHERE name = $1', 'Bob')
        # *row* now contains
        # asyncpg.Record(id=1, name='Bob', dob=datetime.date(1984, 3, 1))

        # Close the connection.

        async with conn.transaction():
            # Postgres requires non-scrollable cursors to be created
            # and used in a transaction.
            async for record in conn.cursor(
                "SELECT * FROM show_show WHERE countries=$1 and release_year=$2", "", 2012
            ):
                print(record)
            
        await conn.close()

asyncio.run(main())