from typing import Any
from pydantic import BaseModel


class Skill(BaseModel):
    """Skill to be used by the agent."""

    name: str
    description: str
    satoshis: int | None = None


class AgentCard(BaseModel):
    """Agent information."""

    name: str
    description: str
    skills: list[Skill] = []
    satoshis: int | None = None
    nostr_pubkey: str
    nostr_relays: list[str] = []


class ChatInput(BaseModel):
    """Chat input."""

    messages: list[str]
    thread_id: str | None = None
    extra_inputs: dict[str, Any] = {}

