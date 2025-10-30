"""
Model Factory - Creating OpenAI Chat Completion Models

This module provides a factory function for creating OpenAI models that work
with the Agent SDK. It centralizes model configuration and makes it easy to
swap models across the entire application.

Key Concepts:
1. Factory Pattern: Single function creates all model instances
2. Async Client: Uses AsyncOpenAI for non-blocking I/O operations
3. SDK Wrapper: OpenAIChatCompletionsModel wraps the raw OpenAI client
4. Default Model: GPT-4.1 as the sensible default for most tasks

💡 A-HA MOMENT: Why use a factory instead of creating clients directly?
- Centralized configuration (change once, affect everywhere)
- Easier testing (mock the factory, not every agent)
- Type safety (returns the Agent SDK's model wrapper)
- Environment management (dotenv loaded in one place)

Model Choices in This Workshop:
- GPT-4.1: Main agents (intent, profiler, evaluator) - best reasoning
- GPT-4.1-mini: Guardrail agent - fast, cheap, sufficient for simple checks

Try This Experiment:
Change the default model to "gpt-4.1-mini" and see how agent behavior changes.
You'll notice faster responses but potentially less nuanced reasoning.
"""

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv

# Load environment variables (OPENAI_API_KEY is required)
# This must be called before creating the AsyncOpenAI client
load_dotenv()


def get_completions_model(model: str = "gpt-4.1") -> OpenAIChatCompletionsModel:
    """
    Factory function to create OpenAI chat completion models for Agent SDK.

    This function wraps the OpenAI AsyncOpenAI client with the Agent SDK's
    OpenAIChatCompletionsModel, which provides:
    - Streaming support for real-time responses
    - Token counting and cost tracking
    - Retry logic and error handling
    - Integration with Agent SDK's Runner

    💡 A-HA MOMENT: Notice we create a NEW client each time!
    This might seem wasteful, but AsyncOpenAI clients are lightweight and
    connection pooling happens internally. Creating per-call clients is
    the recommended pattern for async OpenAI usage.

    Args:
        model: The OpenAI model identifier (default: "gpt-4.1")
               Common options:
               - "gpt-4.1": Latest GPT-4 (best quality, slower, expensive)
               - "gpt-4.1-mini": Smaller GPT-4 (good quality, faster, cheaper)
               - "gpt-4-turbo": Previous generation (still good, less expensive)

    Returns:
        OpenAIChatCompletionsModel: Agent SDK-compatible model wrapper

    Example:
        # Create a model for the main agent
        main_model = get_completions_model(model="gpt-4.1")

        # Create a model for the guardrail (cheaper/faster)
        guardrail_model = get_completions_model(model="gpt-4.1-mini")
    """

    # Create async OpenAI client
    # API key is loaded from OPENAI_API_KEY environment variable
    client = AsyncOpenAI()

    # Wrap the client in the Agent SDK's model wrapper
    # This adds Agent-specific functionality on top of the raw OpenAI client
    model = OpenAIChatCompletionsModel(model=model, openai_client=client)

    return model
