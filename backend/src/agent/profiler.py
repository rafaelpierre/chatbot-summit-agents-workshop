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
    
    Schema for classifying loan details based on user responses.

    Attributes: 
        purpose: The purpose of the loan.
        amount: The desired loan amount.
        term: The preferred loan term.
        credit_score: The credit score range of the user.
        collateral: Whether the user has collateral to offer.
        reasoning: Agent's reasoning behind the classification.
    """

    purpose: Literal[
        "home_purchase",
        "car_purchase",
        "debt_consolidation",
        "business_investment",
        "education",
        "unknown"
    ]
    amount: float
    term: int
    credit_score: Literal[
        "excellent",
        "good",
        "fair",
        "poor",
        "unknown"
    ]
    collateral: bool
    reasoning: str
    next_question: str | None = None


loan_profiler_agent = Agent[ConversationContext](
    name="Loan Profiler Agent",
    instructions=dedent(f"""
        {RECOMMENDED_PROMPT_PREFIX}

        Your job is to ask questions to the user to gather information about their loan needs.
        Based on the user's responses, classify the loan into one of the predefined categories.
        
        ## Questions you need to ask

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
    model_settings=ModelSettings(temperature=0.1, max_tokens=500),
    output_type=LoanClassification,
    input_guardrails=[check_user_input]
)
