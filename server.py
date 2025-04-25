# server.py
from pynostr.filters import FiltersList, Filters
from pynostr.event import EventKind
from pynostr.event import Event
from pynostr.utils import get_public_key
from nostr import relay_manager, public_key, sign
from mcp.server.fastmcp import FastMCP
import uuid


# Create an MCP server
def create_server(mcp: FastMCP):
    @mcp.tool()
    def my_public_key():
        """Return my public key in bech32 format."""
        return public_key.bech32()

    @mcp.tool()
    def retrieve_messages(author: str, event_kind: EventKind = EventKind.TEXT_NOTE, limit: int = 10):
        """Retrieve messages from the relay manager for the given author."""
        filters = FiltersList([Filters(kinds=[event_kind], authors=[get_public_key(author).hex()], limit=limit)])
        subscription_id = uuid.uuid1().hex
        relay_manager.add_subscription_on_all_relays(subscription_id, filters)
        relay_manager.run_sync()
        messages = []
        while relay_manager.message_pool.has_ok_notices():
            ok_msg = relay_manager.message_pool.get_ok_notice()
            print(ok_msg)
        while relay_manager.message_pool.has_events():
            event_msg = relay_manager.message_pool.get_event()
            print(event_msg.event.to_dict())
            messages.append(event_msg)
        return messages

    @mcp.tool()
    def send_message(content: str, event_kind: EventKind = EventKind.TEXT_NOTE, event_id: str = None,
                     author_pubkey: str = None):
        """Send a message to the relay manager. Optionally specify the event kind, event ID, and/or author public key."""
        event = Event(content, kind=event_kind)
        event.add_event_ref(event_id)
        event.add_pubkey_ref(author_pubkey)
        sign(event)
        print(event)
        relay_manager.publish_event(event)
        relay_manager.run_sync()

    return mcp

