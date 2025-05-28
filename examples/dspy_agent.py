import dspy
from agentstr import NostrAgentServer, NoteFilters
from agentstr.a2a import AgentCard, Skill, ChatInput

# Define relays and private key
relays = ['wss://some.relay.io']
private_key = 'nsec...'

# Define Nostr Wallet Connect string to support lightning payments
nwc_str = 'nostr+walletconnect://...'

# Define A2A agent info
agent_info = AgentCard(
    name='Travel Agent',
    description=('This agent can help you book and manage flights.'),
    skills=[Skill(name='book_flight', description='Book a flight on behalf of a user.', satoshis=25),
            Skill(name='show_itinerary', description='Show the itinerary for the user.', satoshis=0),
            Skill(name='pick_flight', description='Pick the best flight that matches users\' request.', satoshis=0),
            Skill(name='cancel_itinerary', description='Cancel an itinerary on behalf of the user.', satoshis=0),
            ],
    satoshis=0,
    nostr_pubkey='npub...',
)

# Define note filters to listen on
note_filters = NoteFilters(
    tags=['travel_agent_ai_request'],
)

# Define DSPy agent (see https://dspy.ai/tutorials/customer_service_agent/ for more info)
agent = dspy.ReAct(
    DSPyAirlineCustomerSerice,
    tools = [
        fetch_flight_info,
        show_itinerary,
        pick_flight,
        book_flight,
        cancel_itinerary
    ]
)

# Define agent callable
def agent_callable(chat_input: ChatInput) -> str:
    return agent(user_request=chat_input.messages[-1]).process_result

# Initialize the server
server = NostrAgentServer(relays=relays, 
                          private_key=private_key, 
                          nwc_str=nwc_str,
                          agent_info=agent_info,
                          agent_callable=agent_callable,
                          note_filters=note_filters)

# Start the server
server.start()