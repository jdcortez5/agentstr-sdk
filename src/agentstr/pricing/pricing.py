from typing import Any, Callable, Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta

from agentstr.logger import get_logger
from agentstr.pricing import (
    PricingStrategy,
    SubscriptionMetadata,
    PricingStrategyHandler,
    PricingStrategyFactory,
)
from agentstr.models import Skill, AgentCard

logger = get_logger(__name__)


class SkillPricing(BaseModel):
    """Abstracts the pricing mechanism for a Skill
    
    Attributes:
        strategy: The pricing strategy to use
        currency: The currency unit (default: satoshis)
        base_price: Base price for the skill
        price_handler: Handler for dynamic pricing calculations
        metadata: Additional pricing-related metadata
    """
    strategy: PricingStrategy
    currency: str = "satoshis"
    base_price: int = 0
    price_handler: Optional[Callable] = None
    metadata: Optional[Dict[str, Any]] = None

    def calculate_price(self, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate the price based on the configured strategy.

        Args:
            usage_data: Optional data needed for certain pricing strategies

        Returns:
            The calculated price in satoshis
        """
        # Create a mapping of strategy to handler
        strategy_handlers = {
            PricingStrategy.FIXED: FixedPricingHandler(),
            PricingStrategy.USAGE_BASED: UsageBasedPricingHandler(),
            PricingStrategy.TIERED: TieredPricingHandler(),
            PricingStrategy.DYNAMIC: DynamicPricingHandler(),
            PricingStrategy.SUBSCRIPTION: SubscriptionPricingHandler(),
        }

        handler = strategy_handlers.get(self.strategy)
        if handler is None:
            raise ValueError(f"Unknown pricing strategy: {self.strategy}")

        return handler.calculate_price(self, usage_data)


class PriceHandler:
    class Response(BaseModel):
        """Response model for the price handler.

        Attributes:
            can_handle: Whether the agent can handle the request
            cost_sats: Total cost in satoshis (0 if free or not applicable)
            user_message: Friendly message to show the user about the action to be taken
            skills_used: List of skills that would be used, if any
        """
        can_handle: bool
        cost_sats: int = 0
        user_message: str = ""
        skills_used: List[str] = []

    def __init__(self, llm_callable: Callable[[str], str]):
        self.llm_callable = llm_callable
        self._chat_history: Dict[str, List[str]] = {}  # Thread id -> List of messages

    def _create_skill_dict(self, agent_card: "AgentCard") -> Dict[str, "Skill"]:
        """Create a dictionary of skills for faster lookups."""
        return {skill.name.lower(): skill for skill in agent_card.skills}

    def _calculate_skill_cost(self, skills_used: List[str], skill_dict: Dict[str, "Skill"]) -> int:
        """Calculate total cost based on skills used."""
        total_cost = 0
        for skill_name in skills_used:
            skill = skill_dict.get(skill_name.lower())
            if skill and skill.pricing.base_price > 0:
                total_cost += skill.pricing.base_price
        return total_cost

    def _calculate_base_cost(self, agent_card: "AgentCard") -> int:
        """Calculate base cost from agent card."""
        return agent_card.satoshis or 0

    def _can_handle_request(self, result: dict) -> bool:
        """Determine if request can be handled."""
        return result.get("can_handle", False)

    def _get_skills_used(self, result: dict) -> List[str]:
        """Extract skills used from result."""
        return result.get("skills_used", [])

    async def handle(self, user_message: str, agent_card: "AgentCard", thread_id: str | None = None) -> "PriceHandler.Response":
        """Determine if an agent can handle a user's request and calculate the cost.

        This function uses an LLM to analyze whether the agent's skills match the user's request
        and returns the cost in satoshis if the agent can handle it.

        Args:
            user_message: The user's request message.
            agent_card: The agent's model card.
            thread_id: Optional thread ID for conversation context.

        Returns:
            PriceHandler.Response
        """

        # Check chat history
        if thread_id:
            if thread_id in self._chat_history:
                user_message = f"{self._chat_history[thread_id]}\n\n{user_message}"
            self._chat_history[thread_id] = user_message

        logger.debug(f"Agent router: {user_message}")
        logger.debug(f"Agent card: {agent_card.model_dump()}")

        # Prepare the prompt for the LLM
        prompt = f"""You are an agent router that determines if an agent can handle a user's request.

Agent Information:
Name: {agent_card.name}
Description: {agent_card.description}

Skills:"""

        for skill in agent_card.skills:
            prompt += f"\n- {skill.name}: {skill.description}"

        prompt += f"\n\nUser Request History: \n\n{user_message}\n\n"
        prompt += """Analyze if the agent can handle this request based on their skills and description and chat history.
Consider both the agent's capabilities and whether the request matches their purpose.

The agent may need to use multiple skills to handle the request. If so, include all
relevant skills.

The user_message should be a friendly, conversational message that:
- Confirms the action to be taken
- Explains what will be done in simple terms
- Asks for confirmation to proceed
- Is concise (1-2 sentences max)

Respond with a JSON object with these fields:
{
    "can_handle": boolean,    # Whether the agent can handle this request
    "user_message": string,   # Friendly message to ask the user if they want to proceed
    "skills_used": [string]   # Names of skills being used, if any
}"""
        logger.debug(f"Prompt: {prompt}")
        try:
            # Get the LLM response
            response = await self.llm_callable(prompt)

            # Seek to first { and last }
            response = response[response.find("{"):response.rfind("}")+1]
            logger.debug(f"LLM response: {response}")

            # Parse the response
            try:
                result = json.loads(response.strip())
                can_handle = self._can_handle_request(result)
                user_message = result.get("user_message", "")

                # Get skills used
                skills_used: List[str] = self._get_skills_used(result)

                # Calculate total cost based on skills used
                skill_dict = self._create_skill_dict(agent_card)
                skill_cost = 0
                
                if can_handle:
                    for skill_name in skills_used:
                        skill = skill_dict.get(skill_name.lower())
                        if skill:
                            skill_cost += skill.pricing.calculate_price()
                
                base_cost = agent_card.satoshis or 0
                total_cost = skill_cost + base_cost

                logger.debug(f"Router response: {can_handle}, {total_cost}, {user_message}, {skills_used}")
                return self.Response(
                    can_handle=can_handle,
                    cost_sats=total_cost,
                    user_message=user_message,
                    skills_used=skills_used,
                )

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing LLM response: {e!s}")
                return self.Response(
                    can_handle=False,
                    cost_sats=0,
                    user_message="Error processing request",
                    skills_used=[],
                )

        except Exception as e:
            logger.error(f"Error in price handler: {e!s}")
            return self.Response(
                can_handle=False,
                cost_sats=0,
                user_message="Error processing request",
                skills_used=[],
            )


def default_price_handler(base_url: str | None = None, api_key: str | None = None, model_name: str | None = None) -> PriceHandler:
    """Create a default price handler using the given LLM parameters."""
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model_name=model_name
    )
    return PriceHandler(llm.call)
