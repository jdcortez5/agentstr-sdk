import threading
from typing import Callable, Any
import json
import time

from pynostr.event import Event

from nostr_agents.nostr_client import NostrClient
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.tools.tool_manager import ToolManager


class NostrMCPServer(object):
    def __init__(self, nostr_client: NostrClient):
        self.client = nostr_client
        self.tool_manager = ToolManager()

    def add_tool(self,
                 fn: Callable[..., Any],
                 name: str | None = None,
                 description: str | None = None):
        self.tool_manager.add_tool(
            fn=fn,
            name=name,
            description=description
        )

    def list_tools(self) -> list[dict[str, Any]]:
        """Define available tools"""
        return [{
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.parameters
        } for tool in self.tool_manager.list_tools()]

    def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Call a tool by name with arguments."""
        tool = self.tool_manager.get_tool(name)
        if not tool:
            raise ToolError(f"Unknown tool: {name}")
        result = tool.fn(**arguments)
        return result

    def _direct_message_callback(self, event: Event, message: str):
        """
        Callback function to handle incoming direct messages.
        :param event: The event object containing the message.
        :param message: The message content.
        """
        # Process the incoming message
        message = message.strip()
        print(f"Request: {message}")
        try:
            request = json.loads(message)
            if request['action'] == 'list_tools':
                response = {
                    "tools": self.list_tools()
                }
            elif request['action'] == 'call_tool':
                tool_name = request['tool_name']
                arguments = request['arguments']
                try:
                    result = self.call_tool(tool_name, arguments)
                    response = {
                        "content": {
                            "type": "text",
                            "text": str(result)
                        }
                    }
                except Exception as e:
                    response = {
                        "content": {
                            "type": "text",
                            "text": str(e)
                        }
                    }
            else:
                response = {
                    "error": f"Invalid action: {request['action']}"
                }
        except Exception as e:
            response = {
                "error": str(e)
            }
        print(f'Response: {response}')
        time.sleep(1)
        thr = threading.Thread(
            target=self.client.send_direct_message_to_pubkey,
            args=(event.pubkey, json.dumps(response)),
        )
        thr.start()

    def start(self):
        self.client.direct_message_listener(
            callback=self._direct_message_callback
        )


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get the environment variables
    relays = os.getenv('NOSTR_RELAYS').split(',')
    private_key = os.getenv('NOSTR_SERVER_PRIVATE_KEY')
    nwc_str = os.getenv('NOSTR_NWC_STR')


    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    def multiply(a: int, b: int) -> int:
        """Multiply two numbers"""
        return a * b

    def get_weather(city: str) -> str:
        """Gets the weather for a city"""
        if city.lower() in {'portland', 'seattle', 'vancouver'}:
            return 'rainy'
        else:
            return 'sunny'

    def get_current_date() -> str:
        """Gets today's date"""
        return time.strftime("%Y-%m-%d")

    def get_current_time() -> str:
        """Gets the time of day"""
        return time.strftime("%H:%M:%S")

    # Create an instance of NostrClient
    client = NostrClient(relays, private_key, nwc_str)
    server = NostrMCPServer(client)
    server.add_tool(add)  # Add by signature alone
    server.add_tool(multiply, name="multiply", description="Multiply two numbers")  # Add by signature and name
    server.add_tool(get_weather)  # Add by signature alone
    server.add_tool(get_current_date)  # Add by signature alone
    server.add_tool(get_current_time)  # Add by signature alone

    server.start()

    '''
    {"action": "list_tools"}
    {"action": "call_tool", "tool_name": "add", "arguments": {"a": 1, "b": 2}}
    {"action": "call_tool", "tool_name": "multiply", "arguments": {"a": 2, "b": 5}}
    '''
