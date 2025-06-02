from dotenv import load_dotenv

load_dotenv()

import os

import dspy

from agentstr import NostrAgentServer
from agentstr.a2a import ChatInput

# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_DSPY_AGENT_NSEC")

llm_base_url = os.getenv("LLM_BASE_URL").rstrip("/v1")
llm_api_key = os.getenv("LLM_API_KEY")
llm_model_name = os.getenv("LLM_MODEL_NAME")


# Define tools
async def divide_by(dividend: float, divisor: float) -> float:
    return dividend / divisor


async def search_wikipedia(query: str) -> list[str]:
    results = await dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")(query, k=3)
    return [x["text"] for x in results]


# Create ReAct agent
react = dspy.ReAct("question -> answer: float", tools=[divide_by, search_wikipedia])


# Configure DSPy
dspy.configure(lm=dspy.LM(model=llm_model_name, api_base=llm_base_url, api_key=llm_api_key, model_type="chat"))


# Define agent callable
async def agent_callable(chat_input: ChatInput) -> str:
    return (await react.acall(question=chat_input.messages[-1])).answer


# Create Nostr Agent Server
async def server():
    server = NostrAgentServer(relays=relays,
                              private_key=private_key,
                              agent_callable=agent_callable)
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(server())
