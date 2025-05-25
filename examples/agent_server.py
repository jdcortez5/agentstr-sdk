from agentstr import NostrAgentServer

# Define relays and private key
relays = ['wss://some.relay.io']
private_key = 'nsec...'

# Define Nostr Wallet Connect string to support lightning payments
nwc_str = 'nostr+walletconnect://...'

# Define agent URL
agent_url = 'http://localhost:8000'

# Create the server
server = NostrAgentServer(
    agent_url=agent_url,
    satoshis=100,  # Satoshis required for agent interaction
    relays=relays,
    private_key=private_key)

# Start the server
server.start()