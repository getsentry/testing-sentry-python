FROM public.ecr.aws/lambda/python:3.11

# Add Sentry Layer
COPY --from=public.ecr.aws/sentry/sentry-python-serverless-sdk:6 /opt/ /opt

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml ${LAMBDA_TASK_ROOT}

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN uv pip install --system --no-cache -r pyproject.toml

ENV SENTRY_INITIAL_HANDLER="lambda_function.handler"
ENV SENTRY_DSN="https://d655584d05f14c58b86e9034aab6817f@o447951.ingest.sentry.io/5461230"
ENV SENTRY_TRACES_SAMPLE_RATE="1.0"

CMD ["sentry_sdk.integrations.init_serverless_sdk.sentry_lambda_handler"]
