import os
from agentstr import NostrMCPServer
from dotenv import load_dotenv

load_dotenv()

# Define relays and private key
relays   = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('EXAMPLE_MCP_SERVER_NSEC')
print(relays)

# Define tools
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

async def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

async def run():
    # Define the server
    server = NostrMCPServer("Math MCP Server", relays=relays, private_key=private_key)

    # Add tools
    server.add_tool(add)
    server.add_tool(multiply, name="multiply", description="Multiply two numbers")

    # Start the server
    await server.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())

