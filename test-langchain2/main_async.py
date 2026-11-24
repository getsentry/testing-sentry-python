import asyncio
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.langchain import LangchainIntegration


@sentry_sdk.trace(name="My async LangChain AI pipeline", attributes={"sentry.op": "ai.pipeline"})
async def my_pipeline(llm):    
    with sentry_sdk.start_span(name="langchain-async"):
        # Async create message
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hi!"),
        ]
        response = await llm.ainvoke(messages)
        print("Response:")
        print(response.dict())

        # Async create streaming message
        print("Response (Stream):")
        async for chunk in llm.astream(messages):
            print(chunk.dict())


async def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        debug=True,
        integrations=[
            LangchainIntegration(), 
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    import random
    models = ["gpt-3.5-turbo", "gpt-4o-mini"]
    selected_model = random.choice(models)
    llm = ChatOpenAI(
        model=selected_model,
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    await my_pipeline(llm)    


asyncio.run(main())