import threading
import json
import time
from typing import Any, List, Callable
from pynostr.event import Event
import requests
from agentstr.a2a import AgentCard, ChatInput
from agentstr.nostr_client import NostrClient
from pydantic import BaseModel


class NoteFilters(BaseModel):
    """Filters for Nostr notes."""

    nostr_pubkeys: list[str] | None = None
    nostr_tags: list[str] | None = None
    followers_only: bool = True


class NostrAgentServer:
    """A server that integrates an external agent with Nostr, handling direct messages.

    This server communicates with an external agent (e.g., a chatbot) via an API and
    processes direct messages received over Nostr, with optional payment requirements.
    """
    def __init__(self, nostr_client: NostrClient = None,
                 relays: List[str] = None, private_key: str = None, nwc_str: str = None, agent_url:str = None, chat_url_path: str = '/chat', info_url_path: str = '/info', agent_info: AgentCard = None, agent_callable: Callable[[ChatInput], str] = None,
                 note_filters: NoteFilters = None):
        """Initialize the agent server. If agent_info and agent_callable are provided, agent_url, chat_url_path, and info_url_path are ignored.

        Args:
            nostr_client: Existing NostrClient instance (optional).
            relays: List of Nostr relay URLs (if no client provided).
            private_key: Nostr private key (if no client provided).
            nwc_str: Nostr Wallet Connect string for payments (optional).
            agent_url: URL of the external agent API (optional).
            chat_url_path: Path to the chat endpoint of the external agent API (optional).
            info_url_path: Path to the info endpoint of the external agent API (optional).
            agent_info: Agent information (optional).
            agent_callable: Callable to handle agent responses (optional).
            note_filters: Filters for listening to Nostr notes (optional).
        """
        self.client = nostr_client or NostrClient(relays=relays, private_key=private_key, nwc_str=nwc_str)
        self.agent_url = agent_url
        self.chat_url_path = chat_url_path
        self.info_url_path = info_url_path
        self.agent_callable = agent_callable or self._chat_http
        self._agent_info = agent_info or self._get_agent_info()
        self.satoshis = self._agent_info.satoshis
        self.note_filters = note_filters

    def _get_agent_info(self) -> AgentCard:
        """Fetch metadata from the agent API.

        Returns:
            AgentCard containing agent metadata.
        """
        response = requests.get(f"{self.agent_url}{self.info_url_path}", headers={'Content-Type': 'application/json'}).json()
        return AgentCard.model_validate(response)

    def agent_info(self) -> AgentCard:
        """Get the agent's metadata.

        Returns:
            AgentCard containing agent metadata.
        """
        return self._agent_info

    def _chat_http(self, chat_input: ChatInput) -> Any:
        """Send a message to the agent and retrieve the response.

        Args:
            chat_input: The chat input to send to the agent.

        Returns:
            Response from the agent, or an error message.
        """
        request = {'messages': chat_input.messages}
        if chat_input.thread_id:
            request['thread_id'] = thread_id
        print(f'Sending request: {json.dumps(request)}')
        response = requests.post(f"{self.agent_url}{self.chat_url_path}", headers={'Content-Type': 'application/json'}, json=request)
        try:
            response.raise_for_status()
            result = response.text.replace('\\n', '\n').strip('"').strip()
        except Exception as e:
            print(f"Error: {e}")
            result = 'Unknown error'
        print(f'Response: {result}')
        return result

    def chat(self, message: str, thread_id: str | None = None) -> Any:
        """Send a message to the agent and retrieve the response.

        Args:
            message: The message to send to the agent.
            thread_id: Optional thread ID for conversation context.

        Returns:
            Response from the agent, or an error message.
        """
        return self.agent_callable(ChatInput(messages=[message], thread_id=thread_id))

    def _direct_message_callback(self, event: Event, message: str):
        """Handle incoming direct messages for agent interaction.

        Args:
            event: The Nostr event containing the message.
            message: The message content.
        """
        if message.strip().startswith('{'):
            print(f'Ignoring non-chat messages')
            return
        message = message.strip()
        print(f"Request: {message}")
        try:
            if self.satoshis > 0:
                invoice = self.client.nwc_client.make_invoice(amt=self.satoshis, desc="Payment for agent")
                response = invoice

                def on_success():
                    print(f"Payment succeeded for agent")
                    result = self.chat(message, thread_id=event.pubkey)
                    response = str(result)
                    print(f'On success response: {response}')
                    thr = threading.Thread(
                        target=self.client.send_direct_message_to_pubkey,
                        args=(event.pubkey, response),
                    )
                    thr.start()

                def on_failure():
                    response = "Payment failed. Please try again."
                    print(f"On failure response: {response}")
                    thr = threading.Thread(
                        target=self.client.send_direct_message_to_pubkey,
                        args=(event.pubkey, response),
                    )
                    thr.start()

                thr = threading.Thread(
                    target=self.client.nwc_client.on_payment_success,
                    kwargs={'invoice': invoice, 'callback': on_success, 'timeout': 120, 'unsuccess_callback': on_failure}
                )
                thr.start()
            else:
                result = self.chat(message, thread_id=event.pubkey)
                response = str(result)
        except Exception as e:
            response = f'Error: {e}'
        print(f'Response: {response}')
        time.sleep(1)
        thr = threading.Thread(
            target=self.client.send_direct_message_to_pubkey,
            args=(event.pubkey, response),
        )
        thr.start()

    def start(self):
        """Start the agent server, updating metadata and listening for direct messages."""
        thr = threading.Thread(
            target=self.client.update_metadata,
            kwargs={'name': 'agent_server', 'display_name': self._agent_info['name'], 'about': json.dumps(self.agent_info())}
        )
        print(f'Updating metadata for {self.client.public_key.bech32()}')
        thr.start()
        time.sleep(3)
        print(f'Starting message listener for {self.client.public_key.bech32()}')
        self.client.direct_message_listener(callback=self._direct_message_callback)
