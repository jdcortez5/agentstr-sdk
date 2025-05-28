from agentstr import NostrRAG

# Define relays
relays   = ['wss://some.relay.io']

# Define LLM base URL and API key
base_url = 'https://api.routstr.com/v1'
api_key  = 'cashuA1DkpMb...'

# Create the RAG instance
rag = NostrRAG(relays=relays,
               llm_model_name='qwen/qwen3-14b',
               llm_base_url=base_url,
               llm_api_key=api_key)

# Query the RAG
print(rag.query(question="What's new with Bitcoin?"))