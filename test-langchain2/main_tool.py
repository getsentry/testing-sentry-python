import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate

import sentry_sdk
from sentry_sdk.ai.monitoring import ai_track
from sentry_sdk.integrations.langchain import LangchainIntegration


@tool
def get_weather(location: str) -> str:
    """Get the current weather in a given location."""
    return f"The weather in {location} is sunny with a high of 23°C."


@tool
def calculate_tip(bill_amount: float, tip_percentage: float) -> float:
    """Calculate tip amount based on bill and percentage."""
    return bill_amount * (tip_percentage / 100)


@ai_track("My sync LangChain tool AI pipeline")
def my_pipeline(llm, tools):
    with sentry_sdk.start_transaction(name="langchain-sync-tool"):
        # Create agent with tools
        # prompt = ChatPromptTemplate.from_messages([
        #     ("system", "You are a helpful assistant that can use tools to help answer questions."),
        #     ("placeholder", "{chat_history}"),
        #     ("human", "{input}"),
        #     ("placeholder", "{agent_scratchpad}"),
        # ])

        agent = create_agent(model=llm, tools=tools, system_prompt="You are a helpful assistant that can use tools to help answer questions")#.with_config(config={"run_name": "MyAgent1"})
        # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Test with weather tool
        result1 = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": "What's the weather like in San Francisco, CA?"}
                ]
            }
        )
        print("Weather Result:")
        print(result1)

        # Test with calculation tool
        result2 = agent.invoke({
            "input": "Calculate a 18% tip on a $45.50 bill"
        })
        print("Tip Calculation Result:")
        print(result2)

        # Test streaming with agent
        print("Streaming Result:")
        for chunk in agent.stream({
            "input": "What's the weather in New York and calculate a 20% tip on $30?"
        }):
            print(chunk)


def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", "local"),
        traces_sample_rate=1.0,
        send_default_pii=True,
        debug=True,
        integrations=[
            LangchainIntegration(include_prompts=True),
        ],
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
