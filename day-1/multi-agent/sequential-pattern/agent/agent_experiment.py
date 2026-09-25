import asyncio

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.workflow import START, Workflow
from google.genai import types
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Outline Agent: creates the initial blog post outline.
outline_agent = LlmAgent(
    name="OutlineAgent",
    model="gemini-3.5-flash",
    instruction="""Create a blog outline for the given topic with:
    1. A catchy headline
    2. An introduction hook
    3. 3-5 main sections with 2-3 bullet points for each
    4. A concluding thought""",
    output_key="blog_outline",
)

# Writer Agent: writes the full blog post based on the outline from the previous agent.
writer_agent = LlmAgent(
    name="WriterAgent",
    model="gemini-3.5-flash",
    instruction="""Following this outline strictly: {blog_outline}
    Write a brief, 200 to 300-word blog post with an engaging and informative tone.""",
    output_key="blog_draft",
)

# Editor Agent: edits and polishes the draft from the writer agent.
editor_agent = LlmAgent(
    name="EditorAgent",
    model="gemini-3.5-flash",
    instruction="""Edit this draft: {blog_draft}
    Your task is to polish the text by fixing any grammatical errors, improving the flow and sentence structure, and enhancing overall clarity.""",
    output_key="final_blog",
)

# Graph-based workflow: the same sequence, but expressed as explicit edges.
blog_pipeline = Workflow(
    name="BlogPipeline",
    description="Run a blog-writing workflow in a strict sequence.",
    edges=[
        (START, outline_agent),
        (outline_agent, writer_agent),
        (writer_agent, editor_agent),
    ],
)

runner = InMemoryRunner(node=blog_pipeline)


async def main():
    response = await runner.run_debug(
        "Write a blog post about the benefits of multi-agent systems for software developers"
    )
    return response


if __name__ == "__main__":
    asyncio.run(main())
