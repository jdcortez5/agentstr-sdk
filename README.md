# Agentstr - Nostr Agent Tools

### Links

[SDK Reference](https://agentstr.com/docs)
[Usage Examples][https://agentstr.com/usage]


## Overview
The agentstr SDK is designed to integrate MCP functionality with the Nostr protocol, enabling developers to create servers and clients that communicate over Nostr's decentralized relay network. It supports:

+ **NostrClient**: A core client for interacting with Nostr relays, handling events, direct messages, and metadata.
+ **NostrMCPServer**: A server that exposes tools (functions) that clients can call, with optional payment requirements in satoshis via Nostr Wallet Connect (NWC).
+ **NostrMCPClient**: A client that discovers and calls tools on an MCP server, handling payments if required.
+ **NostrRAG**: A Retrieval-Augmented Generation (RAG) system for querying Nostr events.
+ **NostrAgentServer**: A server that interacts with an external agent (e.g., a chatbot) and processes direct messages, with optional payment support.
+ **NWCClient**: A client for Nostr Wallet Connect, managing payments and invoices.

The SDK uses the pynostr library for Nostr protocol interactions and supports asynchronous communication, tool management, and payment processing.

## Usage Example
To demonstrate how to use the agentstr SDK, here's an example of setting up an MCP server with mathematical tools and a client to call them:

### MCP Server
```python
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
```

### MCP Client
```python
import os
import json
from dotenv import load_dotenv
from agentstr.nostr_mcp_client import NostrMCPClient
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
```

For more examples, see the [examples](examples) directory.

### Notes
+ **Dependencies**: The SDK relies on `pynostr` for Nostr protocol interactions and `bolt11` for invoice decoding. Ensure these are installed (`pip install pynostr python-bolt11`).
+ **Environment Variables**: The examples use environment variables (`NOSTR_RELAYS`, `MCP_MATH_PRIVATE_KEY`, `NWC_CONN_STR`, etc.) for configuration, loaded via `dotenv`.
+ **Payment Handling**: Tools or agent interactions requiring satoshis use NWC for invoice creation and payment verification.
+ **Threading**: The SDK uses threading for asynchronous operations, such as listening for messages or monitoring payments.
