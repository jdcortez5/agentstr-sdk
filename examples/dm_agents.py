from dotenv import load_dotenv

load_dotenv()

import os
from agentstr import PrivateKey, NostrClient


def private_to_public_key(private_key: str) -> str:
    return PrivateKey.from_nsec(private_key).public_key.bech32()


# Get the environment variables
relays = os.getenv('NOSTR_RELAYS').split(',')
langgraph_agent_private_key = os.getenv('EXAMPLE_LANGGRAPH_AGENT_NSEC')
agno_agent_private_key = os.getenv('EXAMPLE_AGNO_AGENT_NSEC')
dspy_agent_private_key = os.getenv('EXAMPLE_DSPY_AGENT_NSEC')

async def ask_langgraph_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(langgraph_agent_private_key),
        'What is the weather like in San Francisco?' 
    )
    print(response.message)

async def ask_agno_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(agno_agent_private_key),
        'What was the stock price of nvidia 2 years ago?' 
    )
    print(response.message)

async def ask_dspy_agent():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        private_to_public_key(dspy_agent_private_key),
        'What is 9362158 divided by the year of birth of David Gregory of Kinnairdy castle?' 
    )
    print(response.message)

if __name__ == "__main__":
    import asyncio
    #asyncio.run(ask_langgraph_agent())
    #asyncio.run(ask_agno_agent())
    asyncio.run(ask_dspy_agent())