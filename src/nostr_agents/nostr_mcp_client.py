import threading
from typing import Callable, Any
import json
import time

from pynostr.event import Event
from pynostr.key import PrivateKey

from nostr_agents.nostr_client import NostrClient
from mcp.server.fastmcp.exceptions import ToolError


class NostrMCPClient(object):
    def __init__(self, nostr_client: NostrClient, mcp_pubkey: str):
        self.mcp_pubkey = mcp_pubkey
        self.client = nostr_client

    @staticmethod
    def _set_result_callback(res: list):
        def inner(event: Event, message: str):
            try:
                res[0] = json.loads(message)
                return True
            except Exception as e:
                print(f"Error parsing message: {e}")
            return False
        return inner

    def list_tools(self) -> list[dict[str, Any]] | None:
        """Retrieve available tools"""
        thr = threading.Thread(
            target=self.client.send_direct_message_to_pubkey,
            args=(self.mcp_pubkey, json.dumps({
                'action': 'list_tools'
            })),
        )
        thr.start()
        res = [None]
        self.client.direct_message_listener(
            callback=self._set_result_callback(res),
            recipient_pubkey=self.mcp_pubkey,
            timeout=2,
            close_after_first_message=True
        )
        return res[0]

    def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Call a tool by name with arguments."""
        thr = threading.Thread(
            target=self.client.send_direct_message_to_pubkey,
            args=(self.mcp_pubkey, json.dumps({
                'action': 'call_tool',
                'tool_name': name,
                'arguments': arguments
            })),
        )
        thr.start()
        res = [None]
        self.client.direct_message_listener(
            callback=self._set_result_callback(res),
            recipient_pubkey=self.mcp_pubkey,
            timeout=2,
            close_after_first_message=True
        )
        return res[0]





if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get the environment variables
    relays = os.getenv('NOSTR_RELAYS').split(',')
    private_key = os.getenv('NOSTR_CLIENT_PRIVATE_KEY')
    server_public_key = PrivateKey.from_nsec(os.getenv('NOSTR_SERVER_PRIVATE_KEY')).public_key.hex()
    nwc_str = os.getenv('NOSTR_NWC_STR')

    # Create an instance of NostrClient
    client = NostrClient(relays, private_key, nwc_str)
    mcp_client = NostrMCPClient(client, mcp_pubkey=server_public_key)

    tools = mcp_client.list_tools()
    print(f'Found tools:')
    print(json.dumps(tools, indent=4))

    result = mcp_client.call_tool("get_weather", {"city": "Seattle"})
    print(f'The weather in Seattle is: {result["content"]["text"]}')

    result = mcp_client.call_tool("get_current_date", {})
    print(f'The current date is: {result["content"]["text"]}')

    result = mcp_client.call_tool("multiply", {"a": 69, "b": 420})
    print(f'The result of 69 * 420 is: {result["content"]["text"]}')
