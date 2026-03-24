# test-fastapi-with-database

## Prerequisites

- Docker and Docker Compose
- A Sentry DSN

## Running

```bash
SENTRY_DSN=<your-dsn> ./run.sh
```

This starts two containers:
- **db**: PostgreSQL 16 with a `test_multiline` database
- **app**: FastAPI server on port 5000, using a local editable install of `sentry-python` (mounted from `../../sentry-python`)

On first startup, the app creates `users` and `posts` tables and seeds sample data.

## Reproducing the issue

1. Hit the query endpoint:

   ```bash
   curl http://localhost:5000/query
   ```

2. Watch the app container logs for the `[before_send_transaction]` output. The callback attempts to match a multiline SQL string against span descriptions but fails to find a match.
