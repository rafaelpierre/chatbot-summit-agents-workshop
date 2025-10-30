from agents import Runner, SQLiteSession
import asyncio
from phoenix.otel import register
from uuid import uuid4
from textwrap import dedent
from dotenv import load_dotenv

from src.agent.intent import intent_agent
from src.agent.profiler import loan_profiler_agent, LoanClassification
from src.agent.evaluator import product_evaluator_agent, LoanProduct
from src.agent.context import ConversationContext

load_dotenv()

session = SQLiteSession(
    session_id=str(uuid4()),
    db_path=":memory:"
)

"""

Once you have setup PHOENIX_COLLECTOR_ENDPOINT and PHOENIX_API_KEY
in your .env file, uncomment this

tracer_provider = register(
    project_name="<YOUR_PROJECT_NAME>", auto_instrument=True
)
"""

async def run():

    # Context

    context = ConversationContext()

    # Handoffs

    loan_profiler_agent.handoffs = [product_evaluator_agent]
    intent_agent.handoffs = [loan_profiler_agent]

    current_agent = intent_agent
    agent_message = "Hi, how can I help you today?"


    while True:

        print(agent_message)
        prompt = input("Enter your message: ")
        result = await Runner.run(
            starting_agent=current_agent,
            input=prompt,
            context=context,
            session=session
        )

        current_agent = result.last_agent
        print(f"Current agent: {current_agent.name}")
        
        if isinstance(result.final_output, LoanClassification):
            handover_message = "Thanks. Let me handover to our Product Evaluator agent..."
            agent_message = result.final_output.next_question or handover_message
            
        elif isinstance(result.final_output, LoanProduct):

            product_tier = result.final_output.product_tier
            agent_message = dedent(f"""
                Thanks! Your product classification is {product_tier}.\n
                A human agent will get in touch with you shortly.
            """)

            # End the conversation
            return 0


if __name__ == "__main__":

    asyncio.run(run())
