from dotenv import load_dotenv

load_dotenv()

import os

from agentstr import NostrMCPServer

# Define relays and private key
relays   = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_MCP_SERVER_NSEC")

# To enable Nostr Wallet Connect
nwc_str = os.getenv("MCP_SERVER_NWC_CONN_STR")

# Define tools
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

async def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

async def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


async def run():
    # Define the server
    server = NostrMCPServer(
        "Math MCP Server",
        relays=relays,
        private_key=private_key,
        nwc_str=nwc_str,
    )

    # Add tools
    server.add_tool(add) # Free tool
    server.add_tool(multiply, satoshis=3) # Premium tool
    server.add_tool(get_weather) # Free tool

    # Start the server
    await server.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())

