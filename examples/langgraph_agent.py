from langchain_mcp_adapters import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Define relays and private key
relays = ['wss://some.relay.io']
private_key = 'nsec...'

# Define Nostr Wallet Connect string to support lightning payments
nwc_str = 'nostr+walletconnect://...'

# Define MCP server public key
server_public_key = 'npub...'

# Define LLM base URL and API key
base_url = 'https://api.routstr.com/v1'
api_key  = 'cashuA1DkpMb...'

model = ChatOpenAI(temperature=0, 
                   base_url=base_url,
                   api_key=api_key,
                   model_name="gpt-4o")

async def nostr_mcp_agent():
    # Define MCP Server with Nostr transport
    async with MultiServerMCPClient(
        {
            "nostr-math-mcp": {
                "relays": relays,
                "server_public_key": server_public_key,
                "private_key": private_key,
                "nwc_str": nwc_str,
                "transport": "nostr",
            },
        }
    ) as client:
        # Create the agent
        agent = create_react_agent(model, client.get_tools(), checkpointer=MemorySaver())
        yield agent
    
if __name__ == '__main__':
    import asyncio

    # Async function to run the agent
    async def run():
        async with nostr_mcp_agent() as agent:
            async for output in agent.astream({"messages": "what's (4 + 20) * 69?"}, stream_mode="updates"):
                print(output)

    # Run the agent
    asyncio.run(run())