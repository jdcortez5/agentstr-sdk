from pynostr.key import PrivateKey
from agentstr import NostrClient
from dotenv import load_dotenv
import os

load_dotenv()
print(PrivateKey().bech32())
# Define relays
relays = os.getenv('NOSTR_RELAYS').split(',')


async def run():
    client = NostrClient(relays)
    events = await client.read_posts_by_tag('bitcoin', limit=3)
    for event in events:
        print(event.to_dict())


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())