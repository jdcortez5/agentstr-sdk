from dotenv import load_dotenv

load_dotenv()

import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agentstr import ChatInput, NostrAgentServer


# Get the environment variables
relays = os.getenv('NOSTR_RELAYS').split(',')
private_key = os.getenv('EXAMPLE_LANGGRAPH_AGENT_NSEC')

model = ChatOpenAI(temperature=0,
                   base_url=os.getenv('LLM_BASE_URL'),
                   api_key=os.getenv('LLM_API_KEY'),
                   model_name=os.getenv('LLM_MODEL_NAME'))


# Define tools
async def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_react_agent(
    model=model,
    tools=[get_weather],  
    prompt="You are a helpful assistant"  
)

# Define agent callable
async def agent_callable(input: ChatInput) -> str:    
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": input.messages[-1]}]}
    )
    return result["messages"][-1].content
    
# Create Nostr Agent Server
async def server():
    server = NostrAgentServer(relays=relays,
                              private_key=private_key,
                              agent_callable=agent_callable)
    await server.start()
    

if __name__ == '__main__':
    import asyncio
    asyncio.run(server())