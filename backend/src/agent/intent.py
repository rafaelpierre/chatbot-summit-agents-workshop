"""
Intent Agent - The Router of the Multi-Agent System

This agent serves as the entry point and "bouncer" for the loan origination system.
Its job is simple but critical: determine if the user's query is loan-related.

Key Design Decisions:
- Low temperature (0.1): We want deterministic, consistent routing decisions
- Small max_tokens (100): Intent classification shouldn't require long responses
- No output schema: Returns plain text when rejecting non-loan queries
- No input guardrails: This is the first line of defense, so we don't double-check

💡 A-HA MOMENT: Notice this agent does NOT use input_guardrails, even though
it's imported! Only the downstream agents (profiler, evaluator) validate inputs.
This is intentional - we want to quickly route queries before expensive validation.

Try These Test Cases:
1. "I need a loan for a house" → Should hand off to Loan Profiler Agent
2. "What's the weather today?" → Should politely decline
3. "Can you help with credit cards?" → Should politely decline (not loans!)
"""

from agents import Agent, ModelSettings
from src.models.completions import get_completions_model
from src.guardrails.input_guardrails import check_user_input  # Imported but not used
from src.agent.context import ConversationContext
from textwrap import dedent


intent_agent = Agent[ConversationContext](
    name="Intent Investigation Agent",
    instructions=dedent("""
        Your job is to analyze user intents based on their input queries.
        Given a user query, determine the underlying intent.
        If the user's intent is related to financial loans, hand over to the Loan Profiler Agent.
        If not, respond politely indicating that you cannot assist with non-loan related queries.
    """),
    model=get_completions_model(model="gpt-4.1"),
    # Low temperature = more deterministic routing decisions
    # We want consistent behavior when classifying intents
    model_settings=ModelSettings(temperature=0.1, max_tokens=100),
)
