import os
from dotenv import load_dotenv
from agentstr.nostr_mcp_server import NostrMCPServer

load_dotenv()

relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('MCP_MATH_PRIVATE_KEY')

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

server = NostrMCPServer("Math MCP Server", relays=relays, private_key=private_key)
server.add_tool(add)
server.add_tool(multiply, name="multiply", description="Multiply two numbers")
server.start()