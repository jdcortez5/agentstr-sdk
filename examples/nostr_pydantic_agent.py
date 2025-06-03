from dotenv import load_dotenv

load_dotenv()

import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from agentstr import ChatInput, NostrAgentServer, NostrMCPClient
from agentstr.mcp.pydantic import to_pydantic_tools

# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_PYDANTIC_AGENT_NSEC")
mcp_server_pubkey = os.getenv("EXAMPLE_MCP_SERVER_PUBKEY")

# Enable lightning payments
nwc_str = os.getenv("MCP_CLIENT_NWC_CONN_STR")

# Create Nostr MCP client
nostr_mcp_client = NostrMCPClient(relays=relays,
                                  private_key=private_key,
                                  mcp_pubkey=mcp_server_pubkey,
                                  nwc_str=nwc_str)


async def agent_server():
    # Define tools
    pydantic_tools = await to_pydantic_tools(nostr_mcp_client)

    for tool in pydantic_tools:
        print(f'Found {tool.name}: {tool.description}')

    # Define Pydantic agent
    agent = Agent(
        system="You are a helpful assistant.",
        model=OpenAIModel(
            os.getenv("LLM_MODEL_NAME"),
            provider=OpenAIProvider(
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY"),
            )
        ),
        tools=pydantic_tools,
    )

    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        result = await agent.run(input.messages[-1])
        return result.output

    # Create Nostr Agent Server
    server = NostrAgentServer(relays=relays,
                              private_key=private_key,
                              agent_callable=agent_callable,
                              nwc_str=nwc_str)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
