import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.langchain import LangchainIntegration


@tool
def get_weather(location: str) -> str:
    """Get the current weather in a given location."""
    return f"The weather in {location} is sunny with a high of 23°C."


@tool
def calculate_tip(bill_amount: float, tip_percentage: float) -> float:
    """Calculate tip amount based on bill and percentage."""
    return bill_amount * (tip_percentage / 100)


@sentry_sdk.trace(name="My sync LangChain tool AI pipeline", attributes={"sentry.op": "ai.pipeline"})
def my_pipeline(llm, tools):
    with sentry_sdk.start_span(name="langchain-sync-tool"):
        # Create agent with tools
        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="You are a helpful assistant that can use tools to help answer questions",
        ).with_config(config={"run_name": "MyAgent1"})

        # Test with weather tool
        result1 = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "What's the weather like in San Francisco, CA?",
                    }
                ]
            }
        )
        print("Weather Result:")
        print(result1)

        # Test with calculation tool
        result2 = agent.invoke({"input": "Calculate a 18% tip on a $45.50 bill"})
        print("Tip Calculation Result:")
        print(result2)

        # Test streaming with agent
        print("Streaming Result:")
        for chunk in agent.stream(
            {"input": "What's the weather in New York and calculate a 20% tip on $30?"}
        ):
            print(chunk)


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
        temperature=0,
    )

    tools = [get_weather, calculate_tip]

    my_pipeline(llm, tools)


if __name__ == "__main__":
    main()
