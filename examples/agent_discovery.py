from dotenv import load_dotenv

load_dotenv()

import json
import os

from agentstr import NostrClient, AgentCard

# Define relays
relays = os.getenv("NOSTR_RELAYS").split(",")
client = NostrClient(relays)


async def run():
    events = await client.read_posts_by_tag("agentstr_agents", limit=5)
    for event in events:
        metadata = await client.get_metadata_for_pubkey(event.pubkey)
        try:
            agent_info = AgentCard.model_validate_json(metadata.about)
            print(json.dumps(agent_info.model_dump(), indent=4))
        except:
            pass  # Invalid agent card


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
