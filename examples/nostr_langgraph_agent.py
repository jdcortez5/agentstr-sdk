from dotenv import load_dotenv

load_dotenv()

import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agentstr import NostrAgentServer, NostrMCPClient, ChatInput
from agentstr.tools.langgraph import to_langgraph_tools


# Get the environment variables
relays = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_LANGGRAPH_AGENT_NSEC")
mcp_server_pubkey = os.getenv("EXAMPLE_MCP_SERVER_PUBKEY")


nostr_mcp_client = NostrMCPClient(relays=relays,
                                  private_key=private_key,
                                  mcp_pubkey=mcp_server_pubkey)


# Define LLM
model = ChatOpenAI(temperature=0,
                   base_url=os.getenv("LLM_BASE_URL"),
                   api_key=os.getenv("LLM_API_KEY"),
                   model_name=os.getenv("LLM_MODEL_NAME"))


async def agent_server():
    # Convert tools to LangGraph tools
    langgraph_tools = await to_langgraph_tools(nostr_mcp_client)

    for tool in langgraph_tools:
        print(f'Found {tool.name}: {tool.description}')

    # Create react agent
    agent = create_react_agent(
        model=model,
        tools=langgraph_tools,
        prompt="You are a helpful assistant",
    )

    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": input.messages[-1]}]},
        )
        return result["messages"][-1].content

    # Create Nostr Agent Server
    server = NostrAgentServer(relays=relays,
                              private_key=private_key,
                              agent_callable=agent_callable)

    # Start server
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(agent_server())
