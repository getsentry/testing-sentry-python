# Google GenAI / Vertex AI Test

This project demonstrates how to use Google's GenAI API with Vertex AI authentication.

## Prerequisites

1. Python 3.8+
2. Google Cloud Project with Vertex AI API enabled (there is already one in Sentry)
3. Authentication credentials (see setup below)

## Authentication Setup

In shared 1Password there is a shared secret `Vertex API Key JSON` which contains JSON credentials for service account set up.

All the scripts in this directory rely on using that service account as an authentication to Vertex APIs, we don't have an API key.

To set it up, copy the content of the secret to a JSON file, and the path of the file should be store in `GOOGLE_APPLICATION_CREDENTIALS`.

Ask on Slack for the values for `GOOGLE_VERTEX_LOCATION` and `GOOGLE_VERTEX_PROJECT` env variables.

## Configure

Set the following environment variables in `.env` file:

- `SENTRY_DSN`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_VERTEX_LOCATION`
- `GOOGLE_VERTEX_PROJECT`

# Example scripts

Docs are available at README.md in https://github.com/googleapis/python-genai or at https://googleapis.github.io/python-genai/.

- `client.py` - runs the basic example from the docs
- `client_content_stream.py` - runs the content stream example from the documentation
- `client_async.py` - runs the async example from the documentation
- `chats.py` - runs the chats example from the documentation
