from agentstr import NostrClient

# Define relays
relays = ['wss://some.relay.io']

client = NostrClient(relays)

events = client.read_posts_by_tag('mcp_tool_discovery')

for event in events:
    print(event['content'])