"""
Loan Originator Multi-Agent Chat Service

This is the main orchestration layer for a multi-agent loan origination system.
It demonstrates:
1. Agent handoff chains (intent → profiler → evaluator)
2. Structured outputs with Pydantic models
3. Conversation state management with SQLiteSession
4. Phoenix observability integration for agent tracing

The system uses three specialized agents working together:
- Intent Agent: Determines if the user query is loan-related
- Loan Profiler Agent: Gathers detailed loan requirements through conversation
- Product Evaluator Agent: Classifies the user into a product tier (bronze/silver/gold)
"""

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

# Load environment variables (OPENAI_API_KEY, PHOENIX_API_KEY, etc.)
load_dotenv()

# SQLite session for conversation persistence
# Using in-memory database (:memory:) for workshop simplicity
# In production, you would use a persistent database path
# Each conversation gets a unique session_id via UUID
session = SQLiteSession(session_id=str(uuid4()), db_path=":memory:")

"""
🎯 STUDENT EXERCISE: Phoenix Observability Setup

Phoenix by Arize provides LLM observability and tracing for your multi-agent system.
Once enabled, you'll be able to:
- Track which agent handles each conversation turn
- Monitor agent handoffs in real-time
- View input/output for each agent interaction
- Debug agent decision-making processes

Setup Instructions:
1. Sign up for Phoenix at https://phoenix.arize.com
2. Get your PHOENIX_API_KEY from the dashboard
3. Add to your .env file:
   PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/...
   PHOENIX_API_KEY=your_api_key_here
4. Uncomment the code below and replace <YOUR_PROJECT_NAME>
5. Run the application and watch the traces in Phoenix dashboard!

tracer_provider = register(
    project_name="<YOUR_PROJECT_NAME>",  # e.g., "loan-originator-workshop"
    auto_instrument=True  # Automatically instruments OpenAI agents
)
"""


async def run():
    """
    Main conversation loop orchestrating the multi-agent workflow.

    Flow:
    1. Set up shared context for all agents
    2. Configure agent handoff chain
    3. Run conversation loop until loan product is assigned
    4. Handle different output types (LoanClassification vs LoanProduct)
    """
    # Step 1: Initialize shared context
    # This context object is passed to ALL agents and maintains state
    # across the entire conversation (e.g., product_tier classification)
    context = ConversationContext()

    # Step 2: Configure agent handoff chain
    # This creates a directed graph of agent transitions:
    #   Intent Agent → Loan Profiler Agent → Product Evaluator Agent
    #
    # 💡 A-HA MOMENT: Agents can only hand off to agents in their handoffs list!
    # This prevents infinite loops and ensures a clear conversation flow.
    loan_profiler_agent.handoffs = [product_evaluator_agent]
    intent_agent.handoffs = [loan_profiler_agent]

    # Step 3: Start with the Intent Agent
    # This agent acts as a "router" to determine if the query is loan-related
    current_agent = intent_agent
    agent_message = "Hi, how can I help you today?"

    # Step 4: Main conversation loop
    while True:
        print(agent_message)
        prompt = input("Enter your message: ")

        # Runner.run() is the key orchestrator that:
        # - Executes the current agent
        # - Runs input guardrails (if configured)
        # - Handles agent handoffs automatically
        # - Maintains conversation history via session
        result = await Runner.run(
            starting_agent=current_agent, input=prompt, context=context, session=session
        )

        # Track which agent ended up handling this turn
        # This may be different from starting_agent if a handoff occurred!
        current_agent = result.last_agent
        print(f"Current agent: {current_agent.name}")

        # Step 5: Handle structured outputs based on agent type

        # Case 1: Loan Profiler Agent returns LoanClassification
        # This means we're still gathering information OR ready to hand off
        if isinstance(result.final_output, LoanClassification):
            handover_message = (
                "Thanks. Let me handover to our Product Evaluator agent..."
            )
            # 💡 A-HA MOMENT: The agent controls conversation flow via next_question!
            # If next_question is None, we're done profiling and ready to evaluate
            agent_message = result.final_output.next_question or handover_message

        # Case 2: Product Evaluator Agent returns LoanProduct
        # This is our terminal state - the conversation is complete!
        elif isinstance(result.final_output, LoanProduct):
            product_tier = result.final_output.product_tier
            agent_message = dedent(f"""
                Thanks! Your product classification is {product_tier}.\n
                A human agent will get in touch with you shortly.
            """)

            # End the conversation successfully
            return 0

        # Case 3: Intent Agent returns plain text (non-loan-related query)
        # This would typically be a polite rejection or redirect
        else:
            print(result.final_output)


if __name__ == "__main__":
    asyncio.run(run())
