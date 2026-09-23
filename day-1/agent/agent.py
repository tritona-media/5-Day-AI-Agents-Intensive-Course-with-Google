import asyncio

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attemptsget_adk_proxy_url()
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)

runner = InMemoryRunner(agent=root_agent)

async def main():
    response = await runner.run_debug(
        "Who won the last soccer world cup?"
    )

if __name__ == "__main__":
    asyncio.run(main())
