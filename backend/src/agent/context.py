"""
Conversation Context - Shared State Across All Agents

This module defines the shared state that persists throughout the entire
multi-agent conversation. Think of it as a "conversation memory" or "blackboard"
that all agents can read and write to.

Key Concepts:
1. Shared State: All agents in the chain receive the same context instance
2. Pydantic Model: Type-safe state management with validation
3. Default Values: Starts with sensible defaults ("unknown" tier)
4. Mutable: Agents can update fields during the conversation

💡 A-HA MOMENT: This is how agents "remember" things across handoffs!
Without context, each agent would start from scratch. With it, the Product
Evaluator can see what the Loan Profiler learned, even though they're
different agents.

In this simple example, we only track product_tier. In a production system,
you might track:
- conversation_id: Unique identifier for this conversation
- user_profile: Cached user information
- compliance_flags: Regulatory checks that have been performed
- audit_trail: Log of agent decisions for compliance
- session_metadata: Timestamps, channel info, etc.
"""

from pydantic import BaseModel
from typing import Literal


class ConversationContext(BaseModel):
    """
    Shared state container for multi-agent conversations.

    This Pydantic model is passed to ALL agents in the chain via the Runner.
    Each agent can read the current state and update it as needed.

    Attributes:
        product_tier: The assigned loan product tier (set by Product Evaluator)
                     Defaults to "unknown" until evaluation is complete

    💡 A-HA MOMENT: Notice the type is Generic[ConversationContext] in agent definitions!
    This tells the Agent SDK what context type to expect, enabling type safety.

    Example Flow:
    1. Intent Agent runs       → context.product_tier = "unknown"
    2. Loan Profiler runs      → context.product_tier = "unknown" (no change)
    3. Product Evaluator runs  → context.product_tier = "gold" (UPDATED!)
    4. Chat service sees "gold" and ends conversation
    """

    # Literal type constrains values to our 4 valid tiers
    # Default "unknown" indicates no evaluation has occurred yet
    product_tier: Literal["bronze", "silver", "gold", "unknown"] = "unknown"
