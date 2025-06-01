from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

import os
from agentstr import NostrRAG

# Define relays
relays   = os.getenv('NOSTR_RELAYS').split(',')

# Define LLM
model = ChatOpenAI(temperature=0,
                   base_url=os.getenv('LLM_BASE_URL'),
                   api_key=os.getenv('LLM_API_KEY'),
                   model_name=os.getenv('LLM_MODEL_NAME'))

# Create the RAG instance
rag = NostrRAG(relays=relays,
               llm=model)

async def run():
    result = await rag.query(question="What's new with Bitcoin?")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())