from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv

load_dotenv()


def get_completions_model(model: str = "gpt-4.1"):
    client = AsyncOpenAI()

    model = OpenAIChatCompletionsModel(model=model, openai_client=client)

    return model
