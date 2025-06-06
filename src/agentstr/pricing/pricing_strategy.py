from enum import Enum
from typing import Any, Callable, Dict, Optional, List, Type
from datetime import datetime, timedelta
from pydantic import BaseModel

from agentstr.models import Skill, AgentCard
from agentstr.pricing import PricingStrategyFactory


class PricingStrategy(Enum):
    """Enum for different pricing strategies.

    Attributes:
        FIXED: Fixed price per use
        USAGE_BASED: Price varies based on usage
        TIERED: Different prices for different usage tiers
        DYNAMIC: Price calculated dynamically
        SUBSCRIPTION: Subscription-based pricing
    """
    FIXED = "fixed"
    USAGE_BASED = "usage_based"
    TIERED = "tiered"
    DYNAMIC = "dynamic"
    SUBSCRIPTION = "subscription"


class SubscriptionMetadata(BaseModel):
    """Metadata for subscription-based pricing.

    Attributes:
        period: Billing period (daily, weekly, monthly, yearly)
        uses_per_period: Number of uses allowed per period
        renewal_policy: Policy for subscription renewal
        grace_period_days: Number of days after period end before subscription expires
        tier: Subscription tier (basic, premium, etc.)
    """
    period: str  # "daily", "weekly", "monthly", "yearly"
    uses_per_period: int
    renewal_policy: str  # "auto", "manual", "none"
    grace_period_days: int = 0
    tier: str  # "basic", "premium", etc.


class PricingStrategyHandler:
    """Base class for handling specific pricing strategies.

    This class provides a common interface for all pricing strategy implementations.
    Each strategy should inherit from this class and implement the calculate_price method.
    """

    def calculate_price(self, skill: Skill, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate the price for a skill based on the specific strategy.

        Args:
            skill: The skill for which to calculate the price
            usage_data: Optional usage data that might be needed for dynamic pricing

        Returns:
            The calculated price in satoshis
        """
        raise NotImplementedError("This method must be implemented by subclasses")


class FixedPricingHandler(PricingStrategyHandler):
    """Handler for fixed pricing strategy."""

    def calculate_price(self, skill: Skill, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate price for fixed pricing strategy."""
        return skill.pricing.base_price


class UsageBasedPricingHandler(PricingStrategyHandler):
    """Handler for usage-based pricing strategy."""

    def calculate_price(self, skill: Skill, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate price based on usage.

        Args:
            usage_data: Should contain 'usage_count' key with number of uses
        """
        if not usage_data or 'usage_count' not in usage_data:
            raise ValueError("Usage data must contain 'usage_count' for usage-based pricing")
        
        usage_count = usage_data['usage_count']
        return skill.pricing.base_price * usage_count


class TieredPricingHandler(PricingStrategyHandler):
    """Handler for tiered pricing strategy."""

    def calculate_price(self, skill: Skill, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate price based on usage tiers.

        Args:
            usage_data: Should contain 'usage_count' key with number of uses
        """
        if not usage_data or 'usage_count' not in usage_data:
            raise ValueError("Usage data must contain 'usage_count' for tiered pricing")
        
        usage_count = usage_data['usage_count']
        metadata = skill.pricing.metadata or {}
        
        # Example tier structure: [(100, 1000), (50, 500), (25, 250)]
        tiers = metadata.get('tiers', [])
        
        if not tiers:
            return skill.pricing.base_price * usage_count
            
        price = 0
        remaining_usage = usage_count
        
        for tier in tiers:
            if remaining_usage <= 0:
                break
            
            tier_quantity, tier_price = tier
            if remaining_usage >= tier_quantity:
                price += tier_price
                remaining_usage -= tier_quantity
            else:
                price += (remaining_usage / tier_quantity) * tier_price
                break
        
        return int(price)


class DynamicPricingHandler(PricingStrategyHandler):
    """Handler for dynamic pricing strategy.

    Attributes:
        price_handler: Callable function that takes a skill and usage data and returns a price
    """
    price_handler: Callable[[Skill, Optional[Dict[str, Any]]], int]

    def calculate_price(self, skill: Skill, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate price using dynamic pricing handler.

        Args:
            skill: The skill for which to calculate the price
            usage_data: Optional usage data that might be needed for dynamic pricing

        Returns:
            The calculated price in satoshis

        Raises:
            ValueError: If price_handler is not set or returns an invalid value
        """
        if not skill.pricing.price_handler:
            raise ValueError("Dynamic pricing requires a price_handler function")
            
        price = skill.pricing.price_handler(skill, usage_data)
        if not isinstance(price, int):
            raise ValueError(f"Price handler returned invalid type: {type(price)}")
            
        return price


class SubscriptionPricingHandler(PricingStrategyHandler):
    """Handler for subscription-based pricing."""

    def calculate_price(self, skill: Skill, usage_data: Optional[Dict[str, Any]] = None) -> int:
        """Calculate subscription price.

        Args:
            usage_data: Should contain 'subscription_start' and 'current_time'
        """
        if not usage_data or 'subscription_start' not in usage_data:
            raise ValueError("Usage data must contain 'subscription_start' for subscription pricing")
            
        metadata = skill.pricing.metadata
        if not isinstance(metadata, SubscriptionMetadata):
            raise ValueError("Subscription pricing requires SubscriptionMetadata")
            
        # Calculate remaining uses based on period and start time
        start_time = usage_data['subscription_start']
        current_time = usage_data.get('current_time', datetime.now())
        
        if metadata.period == "daily":
            period = timedelta(days=1)
        elif metadata.period == "weekly":
            period = timedelta(weeks=1)
        elif metadata.period == "monthly":
            period = timedelta(days=30)  # Approximate month
        elif metadata.period == "yearly":
            period = timedelta(days=365)
        else:
            raise ValueError(f"Unknown period: {metadata.period}")
            
        time_since_start = current_time - start_time
        periods_elapsed = time_since_start / period
        
        # Calculate remaining uses
        remaining_uses = metadata.uses_per_period * periods_elapsed
        if remaining_uses <= 0:
            return 0  # No remaining uses
            
        return skill.pricing.base_price
