import os

import dotenv

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.langchain import LangchainIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration

dotenv.load_dotenv()

@sentry_sdk.trace(name="My LangChain Core pipeline", attributes={"sentry.op": "ai.pipeline"})
def my_pipeline(llm):    
    with sentry_sdk.start_span(name="langchain-core-demo"):
        # Direct message invocation
        messages = [HumanMessage(content="Hello there! How are you?")]
        response = llm.invoke(messages)
        print("Direct LLM Response:")
        print(response.content)
        print()
        
        # Chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert {domain} consultant."),
            ("human", "I need help with {question}"),
        ])
        
        formatted_messages = chat_prompt.format_messages(
            domain="technology",
            question="understanding AI"
        )
        
        chat_response = llm.invoke(formatted_messages)
        print("Chat Template Response:")
        print(chat_response.content)
        print()
        
        # String prompt template for single string input
        prompt_template = PromptTemplate(
            input_variables=["topic", "style"],
            template="Explain {topic} in a {style} way."
        )
        
        formatted_prompt = prompt_template.format(topic="machine learning", style="simple")
        # Convert to message format
        template_messages = [HumanMessage(content=formatted_prompt)]
        template_response = llm.invoke(template_messages)
        print("Template Response:")
        print(template_response.content)
        print()
        
        # Runnable chain example
        def create_context_message(text: str):
            return [SystemMessage(content="You are a helpful assistant."), HumanMessage(content=f"Question: {text}")]
        
        chain = (
            RunnableLambda(create_context_message)
            | llm
            | StrOutputParser()
        )
        
        chain_result = chain.invoke("Can you help me calculate 15 + 27?")
        print("Chain Response:")
        print(chain_result)
        print()
        
        # Complex runnable with passthrough
        def enhance_input(data):
            enhanced_text = f"Enhanced question: {data['input']} Please provide a detailed response."
            return [HumanMessage(content=enhanced_text)]
        
        complex_chain = (
            RunnablePassthrough.assign(
                enhanced=RunnableLambda(lambda x: f"Enhanced: {x['input']}")
            )
            | RunnableLambda(enhance_input)
            | llm
            | StrOutputParser()
        )
        
        complex_result = complex_chain.invoke({"input": "What's the weather forecast?"})
        print("Complex Chain Response:")
        print(complex_result)


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
        disabled_integrations=[OpenAIIntegration()],
        data_collection={"stack_frame_variables": {"mode": "denylist"}},
        attach_stacktrace=False,
    )

    # Initialize OpenAI LLM
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        api_key=api_key,
        temperature=0.7,
    )
    
    my_pipeline(llm)    


if __name__ == "__main__":
    main()