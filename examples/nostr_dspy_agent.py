from dotenv import load_dotenv
from pynostr.key import PrivateKey

load_dotenv()

import os

import dspy

from agentstr import NostrAgentServer, NostrMCPClient, ChatInput
from agentstr.tools.dspy import to_dspy_tools

# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_DSPY_AGENT_NSEC")
mcp_server_pubkey = os.getenv("EXAMPLE_MCP_SERVER_PUBKEY")
llm_base_url = os.getenv("LLM_BASE_URL").rstrip("/v1")
llm_api_key = os.getenv("LLM_API_KEY")
llm_model_name = os.getenv("LLM_MODEL_NAME")


nostr_mcp_client = NostrMCPClient(relays=relays,
                                  private_key=private_key,
                                  mcp_pubkey=mcp_server_pubkey)


async def agent_server():    
    # Convert tools to DSPy tools
    dspy_tools = await to_dspy_tools(nostr_mcp_client)

    for tool in dspy_tools:
        print(f'Found {tool.name}: {tool.desc}')

    # Create ReAct agent
    react = dspy.ReAct("question -> answer: str", tools=dspy_tools)

    # Configure DSPy
    dspy.configure(lm=dspy.LM(model=llm_model_name, 
                              api_base=llm_base_url, 
                              api_key=llm_api_key, 
                              model_type="chat",
                              temperature=0))

    # Define agent callable
    async def agent_callable(chat_input: ChatInput) -> str:
        return (await react.acall(question=chat_input.messages[-1])).answer

    server = NostrAgentServer(relays=relays,
                              private_key=private_key,
                              agent_callable=agent_callable)
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
