from dotenv import load_dotenv

load_dotenv()

import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

from agentstr import ChatInput, NostrAgentServer

# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_AGNO_AGENT_NSEC")

# Define Agno agent
agent = Agent(
    model=OpenAIChat(
        temperature=0,
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
        id=os.getenv("LLM_MODEL_NAME"),
    ),
    tools=[
        ReasoningTools(add_instructions=True, analyze=True, think=True),
        YFinanceTools(stock_price=True, historical_prices=True), #, analyst_recommendations=True, company_info=True, company_news=True),
    ],
    instructions=[
        "Use tables to display data",
        "Only output the report, no other text",
    ],
    markdown=True,
)

# Define agent callable
async def agent_callable(input: ChatInput) -> str:
    result = await agent.arun(message=input.messages[-1], session_id=input.thread_id)
    return result.content

# Create Nostr Agent Server
async def server():
    server = NostrAgentServer(relays=relays,
                              private_key=private_key,
                              agent_callable=agent_callable)
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(server())
