import os

import asyncpg
import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_USER = os.environ.get("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "postgres")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = os.environ.get("DATABASE_PORT", "5432")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "test_multiline")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


# This multiline string simulates what a user would copy from the Sentry UI
# "Traces" page and paste into their before_send_transaction callback.
# The Sentry UI displays the span description (the SQL query) with its
# original newlines/whitespace intact.
QUERY_TO_FILTER = "SELECT u.id, u.name, u.email, p.title AS post_title, p.created_at AS post_date FROM users u JOIN posts p ON u.id = p.user_id WHERE u.active = true ORDER BY p.created_at DESC"

def before_send_transaction(event, hint):
    """
    User's before_send_transaction callback that attempts to filter out
    transactions containing a specific multiline SQL query.

    The user copied the query string from the Sentry UI Traces page
    and wants to drop transactions that contain this query as a span.
    """
    for span in event.get("spans", []):
        description = span.get("description", "")
        if description and QUERY_TO_FILTER in description:
            logger.info(f"[before_send_transaction] MATCH FOUND - dropping transaction")
            return None

    logger.info(f"[before_send_transaction] No match found - keeping transaction")
    return event


sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "local"),
    traces_sample_rate=1.0,
    debug=True,
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
        AsyncPGIntegration(),
    ],
    before_send_transaction=before_send_transaction,
)

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)

    # Create tables if they don't exist
    async with app.state.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                active BOOLEAN DEFAULT true
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Seed some data if tables are empty
        count = await conn.fetchval("SELECT COUNT(*) FROM users")
        if count == 0:
            await conn.execute("""
                INSERT INTO users (name, email, active) VALUES
                ('Alice', 'alice@example.com', true),
                ('Bob', 'bob@example.com', true),
                ('Charlie', 'charlie@example.com', false)
            """)
            await conn.execute("""
                INSERT INTO posts (user_id, title) VALUES
                (1, 'First Post'),
                (1, 'Second Post'),
                (2, 'Hello World')
            """)


@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()


@app.get("/")
async def root():
    return {
        "endpoints": {
            "multiline_query": "http://localhost:5000/query",
        }
    }


@app.get("/query")
async def multiline_query():
    """
    Executes a multiline SQL query against the database.
    The span description captured by Sentry will contain the query
    with its original newlines.
    """
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("""SELECT
    u.id,
    u.name,
    u.email,
    p.title AS post_title,
    p.created_at AS post_date
FROM
    users u
JOIN
    posts p ON u.id = p.user_id
WHERE
    u.active = true
ORDER BY
    p.created_at DESC""")

        return {
            "count": len(rows),
            "results": [dict(r) for r in rows],
        }
