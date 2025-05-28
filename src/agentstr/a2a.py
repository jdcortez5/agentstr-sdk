from typing import Any
from pydantic import BaseModel


class Skill(BaseModel):
    """Represents a specific capability or service that an agent can perform.

    A Skill defines a discrete unit of functionality that an agent can provide to other
    agents or users. Skills are the building blocks of an agent's service offerings and
    can be priced individually to create a market for agent capabilities.

    Attributes:
        name (str): A unique identifier for the skill that should be descriptive and
            concise. This name is used for referencing the skill in agent interactions.
        description (str): A detailed explanation of what the skill does, including:
            - The specific functionality provided
            - How to use the skill
            - Any limitations or prerequisites
            - Expected inputs and outputs
        satoshis (int, optional): The price in satoshis for using this skill. This allows
            agents to:
            - Set different prices for different capabilities
            - Create premium services
            - Implement usage-based pricing
            If None, the skill is either free or priced at the agent's base rate.
    """

    name: str
    description: str
    satoshis: int | None = None


class AgentCard(BaseModel):
    """Represents an agent's profile and capabilities in the Nostr network.

    An AgentCard is the public identity and capabilities card for an agent in the Nostr
    network. It contains essential information about the agent's services, pricing,
    and communication endpoints.

    Attributes:
        name (str): A human-readable name for the agent. This is the agent's display name.
        description (str): A detailed description of the agent's purpose, capabilities,
            and intended use cases.
        skills (list[Skill]): A list of specific skills or services that the agent can perform.
            Each skill is represented by a Skill model.
        satoshis (int, optional): The base price in satoshis for interacting with the agent.
            If None, the agent may have free services or use skill-specific pricing.
        nostr_pubkey (str): The agent's Nostr public key. This is used for identifying
            and communicating with the agent on the Nostr network.
        nostr_relays (list[str]): A list of Nostr relay URLs that the agent uses for
            communication. These relays are where the agent publishes and receives messages.
    """

    name: str
    description: str
    skills: list[Skill] = []
    satoshis: int | None = None
    nostr_pubkey: str
    nostr_relays: list[str] = []


class ChatInput(BaseModel):
    """Represents input data for an agent-to-agent chat interaction.

    Attributes:
        messages (list[str]): A list of messages in the conversation.
        thread_id (str, optional): The ID of the conversation thread. Defaults to None.
        extra_inputs (dict[str, Any]): Additional metadata or parameters for the chat.
    """

    messages: list[str]
    thread_id: str | None = None
    extra_inputs: dict[str, Any] = {}

