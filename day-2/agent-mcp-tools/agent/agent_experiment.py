import asyncio
from urllib import response
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool

from dotenv import load_dotenv

from IPython.display import display, Image as IPImage
import base64

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

mcp_url_fetch_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",  # Run MCP server via npx
            args=["mcp-server-fetch"]
        ),
        timeout=30,
    )
)

# Create URL fetch agent with MCP integration
root_agent = LlmAgent(
    model=Gemini(model="gemini-3.5-flash", retry_options=retry_config),
    name="url_fetch_agent",
    instruction="""
    Role:
    You are a URL content downloader agent.
    
    Goal:
    Your goal is to fetch content from the provided URL.

    Tasks:
    1. Fetch the content from the given URL using the provided MCP tool.
    2. Summarize the fetched content in a concise manner.
    """,
    tools=[mcp_url_fetch_server],
)

runner = InMemoryRunner(agent=root_agent)

async def main():
    response = await runner.run_debug("Summarize the content from https://de.wikipedia.org/wiki/Allianz_Arena.", verbose=True)

if __name__ == "__main__":
    asyncio.run(main())
