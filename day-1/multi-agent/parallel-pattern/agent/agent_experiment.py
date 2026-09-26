import asyncio

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.adk.workflow import START, Workflow, JoinNode
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Tech Researcher: Focuses on AI and ML trends.
tech_researcher = Agent(
    name="TechResearcher",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config,
    ),
    instruction="""Research the latest AI/ML trends. Include 3 key developments,
the main companies involved, and the potential impact. Keep the report very concise (100 words).""",
    tools=[google_search],
    output_key="tech_research",
)

# Health Researcher: Focuses on medical breakthroughs.
health_researcher = Agent(
    name="HealthResearcher",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config,
    ),
    instruction="""Research recent medical breakthroughs. Include 3 significant advances,
their practical applications, and estimated timelines. Keep the report concise (100 words).""",
    tools=[google_search],
    output_key="health_research",
)

# Finance Researcher: Focuses on fintech trends.
finance_researcher = Agent(
    name="FinanceResearcher",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config,
    ),
    instruction="""Research current fintech trends. Include 3 key trends,
their market implications, and the future outlook. Keep the report concise (100 words).""",
    tools=[google_search],
    output_key="finance_research",
)

# The AggregatorAgent runs after the parallel research step to synthesize the results.
aggregator_agent = Agent(
    name="AggregatorAgent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=retry_config,
    ),
    instruction="""Combine these three research findings into a single executive summary:

    **Technology Trends:**
    {tech_research}

    **Health Breakthroughs:**
    {health_research}

    **Finance Innovations:**
    {finance_research}

    Your summary should highlight common themes, surprising connections, and the most important key takeaways from all three reports. The final summary should be around 200 words.""",
    output_key="executive_summary",
)

join_research = JoinNode(name="join_research")

# Workflow-based graph version of the same parallel research pattern.
research_workflow = Workflow(
    name="ResearchSystem",
    description="Run parallel research on tech, health, and finance, then synthesize the findings.",
    edges=[
        (START, tech_researcher, join_research),
        (START, health_researcher, join_research),
        (START, finance_researcher, join_research),
        (join_research, aggregator_agent)
    ],
)

runner = InMemoryRunner(node=research_workflow)


async def main():
    response = await runner.run_debug(
        "Run the daily executive briefing on Tech, Health, and Finance"
    )
    return response


if __name__ == "__main__":
    asyncio.run(main())
