"""
Product Evaluator Agent - The Decision Maker

This is the final agent in the chain, responsible for risk assessment and product
assignment. It takes the structured data from the Loan Profiler and makes a
business decision: Bronze, Silver, or Gold tier.

Key Features:
1. Simple Output Schema: Only 2 fields (product_tier + reasoning)
2. Clear Decision Criteria: Rules-based evaluation with 3 tiers
3. No Handoffs: This is a terminal agent (conversation ends here)
4. Input Guardrails: Still protected against malicious inputs

💡 A-HA MOMENT: This agent has NO handoffs configured!
Check chat_service.py - product_evaluator_agent.handoffs is never set.
This makes it a "terminal agent" - once it returns output, the conversation ends.

Decision Logic:
- Gold   = Low risk  (excellent credit, good collateral, small amounts)
- Silver = Medium risk (good/fair credit, some collateral, moderate amounts)
- Bronze = High risk (poor credit, no collateral, large amounts)

Try These Test Cases:
1. Excellent credit + $10k loan → Should get Gold tier
2. Poor credit + $200k loan + no collateral → Should get Bronze tier
3. Fair credit + $50k loan + 30% collateral → Should get Silver tier
"""

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
    Structured output schema for product classification.

    This is intentionally simpler than LoanClassification - we only need to
    make a binary decision (which tier?) and explain why.

    💡 A-HA MOMENT: Notice there's NO next_question field here!
    This agent doesn't need to continue the conversation - it makes a final
    decision and the conversation terminates.

    Attributes:
        product_tier: The assigned tier (bronze/silver/gold) based on risk
        reasoning: Transparent explanation for the decision (for compliance/audit)
    """

    product_tier: Literal["bronze", "silver", "gold"]  # 3 risk tiers
    reasoning: str  # Required for explainability and regulatory compliance


product_evaluator_agent = Agent[ConversationContext](
    name="Loan Product Evaluator Agent",
    instructions=dedent(f"""
        {RECOMMENDED_PROMPT_PREFIX}

        Your job is to evaluate the loan application details and make an
        underwriting decision in regards to the loan product type.

        Based on the user's responses, classify the loan into one of the
        predefined categories.

        ## Decision Criteria (Risk-Based Tiering)

        Evaluate applicants across three dimensions: credit score, collateral, and loan amount.
        Use the following guidelines to assign the appropriate tier:

        - Gold (Low Risk):
          * Excellent credit scores (750+)
          * AND/OR sufficient collateral (≥10% of loan value)
          * AND/OR reasonable loan amounts (≤$20,000)

        - Silver (Medium Risk):
          * Good or fair credit scores (650-749)
          * AND/OR some collateral (≥30% of loan value)
          * AND/OR moderate loan amounts ($20,001 - $100,000)

        - Bronze (High Risk):
          * Poor credit scores (<650)
          * AND/OR no collateral or insufficient collateral (<30%)
          * AND/OR high loan amounts (>$100,000)

        💡 Note: Use your judgment to weigh these factors. For example:
        - Excellent credit + no collateral + $15k loan → likely Gold
        - Poor credit + no collateral + $150k loan → definitely Bronze
        - Fair credit + 30% collateral + $50k loan → likely Silver
    """),
    model=get_completions_model(model="gpt-4.1"),
    # Temperature 0.1 = consistent risk evaluation
    # Max tokens 500 = room for detailed reasoning
    model_settings=ModelSettings(temperature=0.1, max_tokens=500),
    # 💡 A-HA MOMENT: Same pattern as Loan Profiler - structured output!
    # This ensures we ALWAYS get a valid tier (bronze/silver/gold) and explanation.
    output_type=LoanProduct,
    # 💡 A-HA MOMENT: Even the final agent uses input guardrails!
    # Defense in depth - we validate at every step, not just at the entry point.
    # This protects against:
    # - Users who managed to bypass intent filtering
    # - Adversarial inputs that try to manipulate the decision
    # - Injection attacks attempting to exfiltrate data
    input_guardrails=[check_user_input],
)
