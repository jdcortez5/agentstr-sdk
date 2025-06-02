import dspy
from functools import partial
from agentstr.nostr_mcp_client import NostrMCPClient


async def to_dspy_tools(nostr_mcp_client: NostrMCPClient) -> list[dspy.Tool]:
    """Convert tools from the MCP client to Dspy tools."""
    tools = await nostr_mcp_client.list_tools()
    return [dspy.Tool(
            name=tool['name'],
            description=tool['description'],
            #satoshis=tool['satoshis'],
            fn=partial(nostr_mcp_client.call_tool, tool['name'])
        ) for tool in tools['tools']]