from dotenv import load_dotenv
from pynostr.key import PrivateKey
from pynostr.relay_manager import RelayManager
from pynostr.event import Event
import os


load_dotenv()

private_key = PrivateKey.from_nsec(os.environ['NOSTR_PRIVATE_KEY'])
public_key = private_key.public_key

relay_manager = RelayManager(timeout=10)

for relay in os.environ['NOSTR_RELAYS'].split(','):
    relay_manager.add_relay(relay.strip(), timeout=10, message_callback=lambda x: print(x))


def sign(event: Event):
    """Sign the event with the private key."""
    event.sign(private_key.hex())
    return event


