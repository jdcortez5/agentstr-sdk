from typing import Any, Callable, Dict, List
from pydantic import BaseModel
from datetime import datetime
import json

from agentstr.logger import get_logger
from agentstr.models import Skill, AgentCard
from agentstr.pricing import SkillPricing, PricingStrategy

logger = get_logger(__name__)


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
