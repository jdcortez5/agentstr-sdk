import os
import json
from agentstr import PrivateKey, NostrMCPClient
from dotenv import load_dotenv

load_dotenv()

# Define relays and private key
relays   = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('EXAMPLE_MCP_CLIENT_NSEC')
nwc_str = os.getenv('TEST_NWC_CONN_STR2')

# Define MCP server public key
server_public_key = PrivateKey.from_nsec(os.getenv('EXAMPLE_MCP_SERVER_NSEC')).public_key.bech32()


async def run()   :
    # Initialize the client
    mcp_client = NostrMCPClient(mcp_pubkey=server_public_key, 
                                relays=relays, 
                                private_key=private_key,
                                nwc_str=nwc_str)

    # List available tools
    tools = await mcp_client.list_tools()
    print(f'Found tools: {json.dumps(tools, indent=4)}')

    # Call a tool
    result = await mcp_client.call_tool("add", {"a": 69, "b": 420})
    print(f'The result of 69 + 420 is: {result["content"][-1]["text"]}')

    # Call a premium tool
    result = await mcp_client.call_tool("multiply", {"a": 69, "b": 420})
    print(f'The result of 69 * 420 is: {result["content"][-1]["text"]}')


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
    