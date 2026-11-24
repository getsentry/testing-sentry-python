import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.langchain import LangchainIntegration


@sentry_sdk.trace(name="My sync LangChain AI pipeline", attributes={"sentry.op": "ai.pipeline"})
def my_pipeline(llm):    
    with sentry_sdk.start_span(name="langchain-sync"):
        # Sync create message
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hi!"),
        ]
        response = llm.invoke(messages)
        print("Response:")
        print(response.dict())

        # Sync create streaming message
        print("Response (Stream):")
        for chunk in llm.stream(messages):
            print(chunk.dict())


def main():
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

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    my_pipeline(llm)    


if __name__ == "__main__":
    main()