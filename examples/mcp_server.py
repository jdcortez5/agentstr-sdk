from agentstr import NostrMCPServer

# Define relays and private key
relays   = ['wss://some.relay.io']
private_key = 'nsec...'

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
