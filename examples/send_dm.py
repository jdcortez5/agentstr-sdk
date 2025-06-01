import os
from agentstr import PrivateKey, NostrClient
from dotenv import load_dotenv

load_dotenv()


# Get the environment variables
relays = os.getenv('NOSTR_RELAYS').split(',')
agent_private_key = os.getenv('EXAMPLE_LANGGRAPH_AGENT_NSEC')


# Send a DM to the server
async def chat():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        PrivateKey.from_nsec(agent_private_key).public_key.bech32(),
        'What is the weather like in San Francisco?' 
    )
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())