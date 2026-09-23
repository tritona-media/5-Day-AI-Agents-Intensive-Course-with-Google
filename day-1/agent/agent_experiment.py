import asyncio

from google.adk.agents import LlmAgent
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

root_agent = LlmAgent(
    name="research_assistant",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config,
    ),
    description="An agent that assists with research tasks.",
    instruction=(
        "You are a research assistant. "
        "For every search result, provide:"
        "- The title"
        "- A one-sentence summary"
        "- The URL"
        "Return the results as a bulleted list."
    ),
    tools=[google_search],
)

runner = InMemoryRunner(agent=root_agent)

async def main():
    response = await runner.run_debug(
        "Search for the latest breaking news in AI."
    )

if __name__ == "__main__":
    asyncio.run(main())
