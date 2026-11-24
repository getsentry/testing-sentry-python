import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_tool_calling_agent


import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.langchain import LangchainIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration


@tool("my_multiply")
def multiply(a: int, b: int) -> int:
    "Multiply two integers."
    return a * b


def main():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", None),
        environment=os.getenv("ENV", os.path.basename(os.getcwd())),
        traces_sample_rate=1.0,
        debug=True,
        integrations=[
            LangchainIntegration(),
            LoggingIntegration(event_level=logging.ERROR, level=None),
        ],
        disabled_integrations=[
            OpenAIIntegration(),
        ],
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    tools = [multiply]

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        model_kwargs={"stream_options": {"include_usage": True}},
        # streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can use tools to help answer questions."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt).with_config({
        "run_name": "MyAgent1",
        "metadata": {
            "agent_name": "MyAgent1.1",
        },
    })

    # agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True).with_config({"run_name": "MyAgent2"})

    with sentry_sdk.start_span(name="langchain-sync"):
        # res = agent_executor.invoke({"input": "What is 12 * 13? Use the tool."}, config={"run_name": "MyAgent3"})
        # print(res["output"])
        for chunk in agent_executor.stream(
            {"input": "What is 12 * 13? Use the tool."},
            config={"run_name": "MyAgent3"}
        ):
            print(chunk)

if __name__ == "__main__":
    main()
