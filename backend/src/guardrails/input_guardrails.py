from agents import (
    Agent,
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
    violates_guidelines: bool
    feedback: str | None


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions=dedent("""
        Your job is to ensure that user inputs adhere to the specified guidelines.
        If an input violates the guidelines, provide constructive feedback.
                        
        Guidelines:
        1. No personal or sensitive information.
        2. No offensive or inappropriate language.
        3. Stay relevant to the topic of financial loans.
    """),
    model=get_completions_model(model="gpt-4.1-mini"),
    model_settings=ModelSettings(temperature=0.1, max_tokens=50),
    output_type=InputGuardrailSchema,
)


@input_guardrail
async def check_user_input(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> InputGuardrailSchema:
    result = await input_guardrail_agent.run(
        input_guardrail_agent, input, context=ctx.context
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.violates_guidelines,
    )
