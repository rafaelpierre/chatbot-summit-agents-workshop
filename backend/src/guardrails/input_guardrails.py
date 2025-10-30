"""
Input Guardrails - The Security Layer

This module implements input validation guardrails using the "agent as guardrail"
pattern. Instead of writing brittle regex rules, we use a small, fast LLM to
evaluate whether user inputs are safe and appropriate.

Key Concepts:
1. Agent as Guardrail: A dedicated mini-agent (GPT-4.1-mini) validates inputs
2. Tripwire Mechanism: If guidelines are violated, the guardrail "trips" and blocks execution
3. Decorator Pattern: @input_guardrail wraps the validation logic
4. Structured Output: Returns both a boolean (violates?) and explanation (why?)

💡 A-HA MOMENT: This is "LLM-protecting-LLM"!
We use a cheap, fast model (GPT-4.1-mini) to validate inputs BEFORE they reach
the expensive main agent (GPT-4.1). This is like having a bouncer check IDs
before people enter the club.

Benefits Over Traditional Validation:
- Semantic understanding (not just keyword matching)
- Context-aware (understands intent, not just words)
- Flexible (adapts to creative adversarial inputs)
- Explainable (provides human-readable feedback)

Trade-offs:
- Adds latency (~200-500ms per input validation)
- Adds cost ($0.15 per 1M tokens for GPT-4.1-mini)
- Non-deterministic (LLMs can occasionally miss edge cases)

Try These Test Cases:
1. "I need a $50k loan for my business" → Should pass (normal query)
2. "My SSN is 123-45-6789, I need a loan" → Should fail (PII violation)
3. "F*** you, give me money" → Should fail (offensive language)
4. "What's the weather today?" → Should fail (off-topic)
"""

from agents import (
    Agent,
    Runner,
    ModelSettings,
    input_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    TResponseInputItem,
)
from src.models.completions import get_completions_model
from textwrap import dedent
from pydantic import BaseModel


class InputGuardrailSchema(BaseModel):
    """
    Structured output for guardrail validation results.

    The guardrail agent returns this schema to indicate:
    1. Whether the input violates guidelines (boolean flag)
    2. Why it was flagged (optional feedback string)

    Attributes:
        violates_guidelines: True if input breaks rules, False if safe
        feedback: Human-readable explanation of the violation (or None if safe)
    """

    violates_guidelines: bool
    feedback: str | None


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions=dedent("""
        Your job is to ensure that user inputs adhere to the specified guidelines.
        If an input violates the guidelines, provide constructive feedback.

        Guidelines:
        1. No personal or sensitive information (SSN, credit card numbers, passwords, etc.)
        2. No offensive or inappropriate language (profanity, hate speech, threats)
        3. Stay relevant to the topic of financial loans (reject off-topic queries)

        Return:
        - violates_guidelines: true if ANY guideline is broken, false otherwise
        - feedback: Brief explanation of what was violated (or null if input is safe)
    """),
    # 💡 A-HA MOMENT: We use GPT-4.1-mini instead of GPT-4.1!
    # Guardrail checks don't need advanced reasoning - they're binary decisions.
    # Using a smaller model reduces latency (faster) and cost (cheaper).
    model=get_completions_model(model="gpt-4.1-mini"),
    # Temperature 0.1 = consistent validation (we want deterministic safety checks)
    # Max tokens 50 = just enough for boolean + short feedback
    model_settings=ModelSettings(temperature=0.1, max_tokens=50),
    # Structured output ensures we ALWAYS get a boolean and optional explanation
    output_type=InputGuardrailSchema,
)


@input_guardrail
async def check_user_input(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Input guardrail function that validates user inputs before agent processing.

    This function is decorated with @input_guardrail, which tells the Agent SDK
    to run this validation BEFORE executing the main agent. It's essentially
    inserting a security checkpoint into the execution flow.

    Flow:
    1. User sends input → Runner.run() receives it
    2. BEFORE main agent runs, this function executes
    3. Guardrail agent (GPT-4.1-mini) analyzes the input
    4. If violates_guidelines=True, the tripwire triggers
    5. If tripwire triggers, main agent is NEVER called (execution halts)
    6. User receives feedback about why their input was rejected

    💡 A-HA MOMENT: The tripwire_triggered field is the "kill switch"!
    When True, it stops the entire agent execution. This is how we prevent
    malicious inputs from ever reaching the main application logic.

    Args:
        ctx: Wrapper containing conversation context and metadata
        agent: The agent this guardrail is protecting (profiler or evaluator)
        input: The raw user input to validate (text or structured messages)

    Returns:
        GuardrailFunctionOutput with:
        - output_info: The validation results (InputGuardrailSchema)
        - tripwire_triggered: Whether to halt execution (True if violated)
    """

    # Run the guardrail agent synchronously (blocking validation)
    result = await Runner.run(input_guardrail_agent, input, context=ctx.context)

    # 💡 A-HA MOMENT: See how we map the schema to the tripwire?
    # If violates_guidelines=True → tripwire_triggered=True → execution halts!
    # This elegant mapping makes it impossible to accidentally allow bad inputs.
    return GuardrailFunctionOutput(
        output_info=result.final_output,  # Contains the full validation schema
        tripwire_triggered=result.final_output.violates_guidelines,  # The kill switch
    )
