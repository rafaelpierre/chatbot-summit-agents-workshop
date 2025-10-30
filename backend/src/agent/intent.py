from agents import Agent, ModelSettings
from src.models.completions import get_completions_model
from src.guardrails.input_guardrails import check_user_input
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
    model_settings=ModelSettings(temperature=0.1, max_tokens=100),
)
