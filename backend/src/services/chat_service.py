from agents import Runner, SQLiteSession
from src.agent.intent import intent_agent
from src.agent.profiler import loan_profiler_agent, LoanClassification
import asyncio
from uuid import uuid4

session = SQLiteSession(
    session_id=str(uuid4()),
    db_path=":memory:"
)


async def run():

    # Handoffs

    intent_agent.handoffs = [loan_profiler_agent]
    loan_profiler_agent.handoffs = [intent_agent]

    # Agentic loop

    num_turns = 0
    max_turns = 10

    while num_turns < max_turns:

        if num_turns == 0:
            agent_message = "Hi, how can I assist you today?"
            current_agent = intent_agent

        print(agent_message)
        prompt = input("Answer: ")
        result = await Runner.run(current_agent, prompt, session=session)
        
        if isinstance(result.final_output, LoanClassification):

            agent_message = result.final_output.next_question
            if not agent_message:
                print("Thank you for the information. Based on your responses, we have classified your loan needs.")
                return 0
        
        num_turns += 1


if __name__ == "__main__":

    asyncio.run(run())
