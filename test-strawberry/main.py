import asyncio
import os
from typing import AsyncGenerator

import sentry_sdk
import strawberry
from fastapi import FastAPI
from sentry_sdk.integrations.strawberry import StrawberryIntegration
from strawberry.fastapi import GraphQLRouter

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV", "test"),
    traces_sample_rate=1.0,
    trace_lifecycle="stream",
    profiles_sample_rate=1.0,
    debug=True,
    integrations=[
        StrawberryIntegration(async_execution=True),
    ],
)


@strawberry.type
class Book:
    title: str
    author: str
    year: int


books_db: list[Book] = [
    Book(title="Oryx and Crake", author="Margaret Atwood", year=2003),
    Book(title="I, Robot", author="Isaac Asimov", year=1950),
    Book(title="A Closed and Common Orbit", author="Becky Chambers", year=2016),
]


@strawberry.type
class AddBookResult:
    success: bool
    book: Book


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Strawberry GraphQL!"

    @strawberry.field
    def books(self) -> list[Book]:
        return books_db

    @strawberry.field
    def book_by_title(self, title: str) -> Book:
        for book in books_db:
            if book.title.lower() == title.lower():
                return book
        raise ValueError(f"Book not found: {title}")

    @strawberry.field
    def error(self) -> str:
        raise ValueError("help! an error!")


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str, year: int) -> AddBookResult:
        book = Book(title=title, author=author, year=year)
        books_db.append(book)
        return AddBookResult(success=True, book=book)

    @strawberry.mutation
    def delete_all_books(self) -> bool:
        books_db.clear()
        return True

    @strawberry.mutation
    def mutation_error(self) -> str:
        raise RuntimeError("mutation failed!")


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def countdown(self, start: int = 5) -> AsyncGenerator[int, None]:
        for i in range(start, 0, -1):
            yield i
            await asyncio.sleep(1)

    @strawberry.subscription
    async def subscription_error(self) -> AsyncGenerator[str, None]:
        yield "starting..."
        raise RuntimeError("subscription exploded!")


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)

graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
