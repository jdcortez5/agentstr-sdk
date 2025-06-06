from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from agentstr.models.skill import Skill
from agentstr.pricing import SkillPricing, PricingStrategy


class AgentCard(BaseModel):
    """Represents an agent's profile and capabilities in the Nostr network.

    An AgentCard is the public identity and capabilities card for an agent in the Nostr
    network. It contains essential information about the agent's services, pricing,
    and communication endpoints.

    Attributes:
        name: A human-readable name for the agent
        description: A detailed description of the agent's purpose, capabilities,
            and intended use cases
        skills: A list of specific skills or services that the agent can perform
        nostr_pubkey: The agent's Nostr public key
        nostr_relays: A list of Nostr relay URLs that the agent uses for communication
        base_pricing: Optional pricing configuration for the agent
        metadata: Additional metadata about the agent
    """
    name: str
    description: str
    skills: List[Skill] = []
    nostr_pubkey: str
    nostr_relays: List[str] = []
    base_pricing: Optional[SkillPricing] = None
    metadata: Optional[Dict[str, Any]] = None

    @property
    def base_price(self) -> int:
        """Get the base price in satoshis."""
        if self.base_pricing:
            return self.base_pricing.base_price
        return 0

    @property
    def pricing_strategy(self) -> Optional[PricingStrategy]:
        """Get the base pricing strategy."""
        if self.base_pricing:
            return self.base_pricing.strategy
        return None

    def calculate_base_cost(self) -> int:
        """Calculate the base cost for this agent."""
        if self.base_pricing:
            return self.base_pricing.calculate_price()
        return 0

    class Config:
        arbitrary_types_allowed = True