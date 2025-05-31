from agentstr.nostr_event_relay import EventRelay
from pynostr.key import PrivateKey
from pynostr.event import EventKind
from pynostr.filters import Filters


if __name__ == '__main__':
    
    event_relay = EventRelay('wss://relay.primal.net', PrivateKey())
    event_relay2 = EventRelay('wss://relay.primal.net', PrivateKey())
    events = event_relay.get_events(Filters(kinds=[EventKind.TEXT_NOTE], limit=5), limit=5)
    for event in events:
        print(event)
    print(len(events))