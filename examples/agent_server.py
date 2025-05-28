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
    relays=relays,
    private_key=private_key,
    nwc_str=nwc_str)

# Start the server
server.start()