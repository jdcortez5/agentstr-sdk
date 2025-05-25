import os
from dotenv import load_dotenv
from agentstr import NostrRAG

load_dotenv()

relays = os.getenv('NOSTR_RELAYS').split(',')

rag = NostrRAG(relays=relays,
               llm_model_name='qwen/qwen3-14b',
               llm_base_url='https://api.routstr.com/v1',
               llm_api_key=os.getenv('ROUTSTR_API_KEY'))

print(rag.query(question="What's new with Bitcoin?"))