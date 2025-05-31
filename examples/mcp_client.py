from agentstr import NostrMCPClient

# Define relays and private key
relays = ['wss://some.relay.io']
private_key = 'nsec...'

# Define MCP server public key
server_public_key = 'npub...'

# Initialize the client
mcp_client = NostrMCPClient(mcp_pubkey=server_public_key, relays=relays, private_key=private_key)

# List available tools
tools = mcp_client.list_tools()
print(f'Found tools: {json.dumps(tools, indent=4)}')

# Call a tool
result = mcp_client.call_tool("multiply", {"a": 69, "b": 420})
print(f'The result of 69 * 420 is: {result["content"][-1]["text"]}')