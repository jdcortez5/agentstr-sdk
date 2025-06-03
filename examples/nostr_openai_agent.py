from dotenv import load_dotenv

load_dotenv()

import os

from agents import Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel
from agentstr import ChatInput, NostrAgentServer, NostrMCPClient
from agentstr.mcp.openai import to_openai_tools

# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_OPENAI_AGENT_NSEC")
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
    openai_tools = await to_openai_tools(nostr_mcp_client)

    for tool in openai_tools:
        print(f'Found {tool.name}: {tool.description}')

    # Define OpenAI agent
    agent = Agent(
        name="OpenAI Agent",
        instructions="You are a helpful assistant.",
        model=OpenAIChatCompletionsModel(
            model=os.getenv("LLM_MODEL_NAME"),
            openai_client=AsyncOpenAI(
                base_url=os.getenv("LLM_BASE_URL"),
                api_key=os.getenv("LLM_API_KEY"),
            )
        ),
        tools=openai_tools,
    )

    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        result = await Runner.run(agent, input=input.messages[-1])
        return result.final_output

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