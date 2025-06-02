from agentstr.nostr_mcp_client import NostrMCPClient
from agno.tools import Function
from functools import partial


async def to_agno_tools(nostr_mcp_client: NostrMCPClient) -> list[Function]:
    """Convert tools from the MCP client to Agno tools."""
    tools = await nostr_mcp_client.list_tools()
    return [Function(
            name=tool['name'],
            description=tool['description'],
            parameters=tool['inputSchema'],
            entrypoint=partial(nostr_mcp_client.call_tool, tool['name'])
        ) for tool in tools['tools']]
    