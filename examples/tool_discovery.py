from dotenv import load_dotenv
load_dotenv()

import os
import json
from agentstr import NostrClient

# Define relays
relays = os.getenv('NOSTR_RELAYS').split(',')


async def run():
    client = NostrClient(relays)
    events = await client.read_posts_by_tag('mcp_research_tools', limit=2)
    for event in events:
        metadata = await client.get_metadata_for_pubkey(event.pubkey)
        try:
            mcp_definition = json.loads(metadata.about)
            print(json.dumps(mcp_definition, indent=4))
        except:
            pass


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())