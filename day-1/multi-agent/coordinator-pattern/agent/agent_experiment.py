import asyncio

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, google_search
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

python_code_agent = Agent(
    name="PythonCodeAgent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config
    ),
    instruction="""You are a Python code agent.
    Goal:
    Generate Python code based on the user's request.
    
    Task:
    1. Read the user's request.
    2. Generate Python code that fulfills the request.
    3. Return Python code and Python code only, without any strings before or after the code.""",
    output_key="python_code",
)

python_code_review_agent = Agent(
    name="PythonCodeReviewerAgent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config
    ),
    instruction="""You are a Python code review agent.
    Goal:
    Review the following Python code and make it as concise and efficient as possible: 
    ---
    {python_code}
    ---

    Task:
    1. Read the provided Python code.
    2. Identify any inefficiencies, redundancies, or areas for improvement.
    3. Rewrite the code to be more concise and efficient while maintaining its original functionality.""",
    output_key="reviewed_python_code",
)

# Root Coordinator: Orchestrates the workflow by calling the sub-agents as tools.
root_agent = Agent(
    name="PythonCodeCoordinator",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config
    ),
    # This instruction tells the root agent HOW to use its tools (which are the other agents).
    instruction="""You are a Python code agent coordinator.
    Goal:
    Produce a final, reviewed Python solution that matches the user's request.

    Task:
    1. Read the user's request.
    2. Use the PythonCodeAgent to generate Python code based on the request.
    3. Use the PythonCodeReviewerAgent to review and improve the generated code.
    4. Return the final reviewed Python code to the user.
    """,
    # We wrap the sub-agents in `AgentTool` to make them callable tools for the root agent.
    tools=[AgentTool(python_code_agent), AgentTool(python_code_review_agent)],
)

runner = InMemoryRunner(agent=root_agent)

async def main():
    response = await runner.run_debug(
        "Write a Python function that takes a string and capitalizes every odd-indexed character."
    )

if __name__ == "__main__":
    asyncio.run(main())
