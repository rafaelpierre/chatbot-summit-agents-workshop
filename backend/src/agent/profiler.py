"""
Loan Profiler Agent - The Information Gatherer

This agent is the heart of the loan origination process. It conducts a structured
interview with the user to collect all necessary information for loan evaluation.

Key Features:
1. Structured Output: Uses Pydantic schema to ensure type-safe data collection
2. Conversational Flow: Controls the conversation via next_question field
3. Input Validation: Protected by input_guardrails to prevent abuse
4. Literal Types: Constrains values to predefined categories (no free-form chaos!)

💡 A-HA MOMENT: The next_question field is the secret sauce!
- If next_question is NOT None: Continue the conversation (ask the question)
- If next_question IS None: All info collected, ready to hand off to evaluator

This pattern allows the agent to control pacing without external orchestration.

Try These Test Cases:
1. Answer all 5 questions sequentially → Watch next_question change
2. Try to inject sensitive data like SSN → Input guardrail should block it
3. Give vague answers → Agent should ask clarifying follow-ups
"""

from agents import Agent, ModelSettings
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from textwrap import dedent
from pydantic import BaseModel
from typing import Literal

from src.models.completions import get_completions_model
from src.guardrails.input_guardrails import check_user_input
from src.agent.context import ConversationContext


class LoanClassification(BaseModel):
    """
    Structured output schema for loan profiling.

    This Pydantic model enforces strict typing and validation on the agent's output.
    Instead of parsing free-form text, we get structured JSON that's ready for downstream
    processing.

    💡 A-HA MOMENT: Using Literal types creates a "closed world" - the agent MUST
    choose from predefined values. This prevents hallucinations like inventing
    new loan purposes or credit score tiers!

    Attributes:
        purpose: The purpose of the loan (constrained to 6 categories + unknown)
        amount: The desired loan amount in dollars (float for cents precision)
        term: The preferred loan term in months (int for exact duration)
        credit_score: The credit score range (constrained to 4 tiers + unknown)
        collateral: Whether the user has collateral (binary yes/no decision)
        reasoning: Agent's explanation for the classification (for transparency)
        next_question: Next question to ask, or None if profiling is complete
    """

    # Literal types ensure the agent picks from a fixed set of values
    purpose: Literal[
        "home_purchase",
        "car_purchase",
        "debt_consolidation",
        "business_investment",
        "education",
        "unknown",
    ]
    amount: float  # Using float to support cents (e.g., $10,250.50)
    term: int  # Number of months (e.g., 12, 24, 36)
    credit_score: Literal["excellent", "good", "fair", "poor", "unknown"]
    collateral: bool  # Simple binary: has collateral or doesn't
    reasoning: str  # Required for explainability and debugging
    next_question: str | None = None  # None signals "profiling complete"


loan_profiler_agent = Agent[ConversationContext](
    name="Loan Profiler Agent",
    instructions=dedent(f"""
        {RECOMMENDED_PROMPT_PREFIX}

        Your job is to ask questions to the user to gather information about their loan needs.
        Based on the user's responses, classify the loan into one of the predefined categories.

        ## Questions you need to ask (5 key data points)

        1. What is the purpose of the loan? (e.g., home purchase, car purchase, debt consolidation, business investment, education, etc.)
        2. What is the desired loan amount?
        3. What is the preferred loan term? (e.g., 12 months, 24 months, 36 months, etc.)
        4. What is your credit score range? (e.g., excellent, good, fair, poor)
        5. Do you have any collateral to offer for the loan? (e.g., property, vehicle, savings, etc.)

        Based on the user's responses, classify the loan details into the appropriate categories.

        You need to provide the following information:

        purpose: The purpose of the loan.
        amount: The desired loan amount.
        term: The preferred loan term.
        credit_score: The credit score range of the user.
        collateral: Whether the user has collateral to offer.
        reasoning: Your explanation on why you classified the loan in this way.
        next_question: If you need more information to complete the classification, provide the next question to ask the user.

        If you have all the information, hand over to the product_evaluator_agent.
    """),
    model=get_completions_model(model="gpt-4.1"),
    # Temperature 0.1 = consistent questioning pattern
    # Max tokens 500 = enough room for question + structured output
    model_settings=ModelSettings(temperature=0.1, max_tokens=500),
    # 💡 A-HA MOMENT: output_type forces structured JSON responses!
    # Without this, we'd get free-form text that's hard to parse and validate.
    # With it, the LLM MUST conform to the LoanClassification schema.
    output_type=LoanClassification,
    # 💡 A-HA MOMENT: input_guardrails run BEFORE the agent processes input!
    # This is like having a security guard check IDs before entering the building.
    # The check_user_input guardrail validates:
    # - No personal/sensitive information (PII, SSN, etc.)
    # - No offensive language
    # - Topic relevance to loans
    input_guardrails=[check_user_input],
)
