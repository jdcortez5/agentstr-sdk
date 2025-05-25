import os
import json
from dotenv import load_dotenv
from agentstr import NostrMCPClient
from pynostr.key import PrivateKey

load_dotenv()

relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('AGENT_PRIVATE_KEY')
server_public_key = PrivateKey.from_nsec(os.getenv('MCP_MATH_PRIVATE_KEY')).public_key.bech32()

mcp_client = NostrMCPClient(mcp_pubkey=server_public_key, relays=relays, private_key=private_key)

tools = mcp_client.list_tools()
print(f'Found tools:')
print(json.dumps(tools, indent=4))

result = mcp_client.call_tool("multiply", {"a": 69, "b": 420})
print(f'The result of 69 * 420 is: {result["content"][-1]["text"]}')