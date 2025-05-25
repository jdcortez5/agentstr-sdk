import os
from dotenv import load_dotenv
from agentstr import NostrMCPServer

load_dotenv()

# Define relays and private key
relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('MCP_MATH_PRIVATE_KEY')

# Define tools
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Define the server
server = NostrMCPServer("Math MCP Server", relays=relays, private_key=private_key)

# Add tools
server.add_tool(add)
server.add_tool(multiply, name="multiply", description="Multiply two numbers")

# Start the server
server.start()
