from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class Skill(BaseModel):
    """Represents a skill or capability that an agent can perform.

    Attributes:
        name: The name of the skill
        description: A description of what the skill does
        pricing: The pricing configuration for this skill
        metadata: Additional metadata about the skill
    """
    name: str
    description: str
    pricing: "SkillPricing"
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True