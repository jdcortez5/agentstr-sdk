import os
from dotenv import load_dotenv
from agentstr import NostrClient

load_dotenv()

relays = os.getenv('NOSTR_RELAYS').split(',')

client = NostrClient(relays)

events = client.read_posts_by_tag('mcp_tool_discovery')

for event in events:
    print(event['content'])