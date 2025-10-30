from agents import Agent, ModelSettings
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from textwrap import dedent
from pydantic import BaseModel
from typing import Literal

from src.models.completions import get_completions_model
from src.guardrails.input_guardrails import check_user_input
from src.agent.context import ConversationContext


class LoanProduct(BaseModel):
    """
    Schema for loan risk evaluation based on application details.
    Attributes:
        risk_profile: The risk profile of the loan application.
        reasoning: Agent's reasoning behind the decision.
    """

    product_tier: Literal["bronze", "silver", "gold"]
    reasoning: str


product_evaluator_agent = Agent[ConversationContext](
    name="Loan Product Evaluator Agent",
    instructions=dedent(f"""
        {RECOMMENDED_PROMPT_PREFIX}

        Your job is to evaluate the loan application details and make an
        underwriting decision in regards to the loan product type.

        Based on the user's responses, classify the loan into one of the
        predefined categories.
        
        ## Decision Criteria

        - Gold: Applicants with excellent credit scores and/or sufficient collateral
            (e.g. 10% of the loan value), and/or reasonable loan amounts (20k or less)
        - Silver: Applicants with good or fair credit scores, and/or 
            some collateral (e.g. 30% of the loan value) and/or moderate loan amounts
        (more than 20k, less than 100k)
        - Bronze: Applicants with poor credit scores and/or no collateral,
            and/or high loan amounts (more than 100k)
    """),
    model=get_completions_model(model="gpt-4.1"),
    model_settings=ModelSettings(temperature=0.1, max_tokens=500),
    output_type=LoanProduct,
    input_guardrails=[check_user_input],
)
