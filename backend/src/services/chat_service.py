from agents import Runner
from src.agent.intent import intent_agent
import asyncio


async def run(prompt: str):


    result = await Runner.run(intent_agent, prompt)
    print("Final Output:", result.final_output)


if __name__ ==  "__main__":

    prompt = input("Enter your question: ")
    asyncio.run(run(prompt))
