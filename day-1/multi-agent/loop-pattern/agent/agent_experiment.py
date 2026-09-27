import asyncio

from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner
from google.adk.workflow import START, Workflow, FunctionNode
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def exit_loop():
    """Terminate the story-refinement loop when the story is approved."""
    return {"status": "approved", "message": "Story approved. Exiting refinement loop."}


# Initial draft: produce the first version of the story.
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model="gemini-3.5-flash",
    instruction="""Based on the user's prompt, write the first draft of a short story (around 100-150 words).
    Output only the story text, with no introduction or explanation.""",
    output_key="current_story",
)

# Critic: if the story is complete, emit the approval route; otherwise emit a revision route.
critic_agent = LlmAgent(
    name="CriticAgent",
    model="gemini-3.5-flash",
    instruction="""You are a constructive story critic. Review the story provided below.
    Story: {current_story}

    Evaluate the story's plot, characters, and pacing.
    - If the story is well-written and complete, you MUST respond with the exact phrase: "APPROVED"
    - Otherwise, provide 2-3 specific, actionable suggestions for improvement.""",
    output_key="critique",
)

# Refiner: revise the story until the critique is approved.
refiner_agent = LlmAgent(
    name="RefinerAgent",
    model="gemini-3.5-flash",
    instruction="""You are a story refiner. You have a story draft and critique.

    Story Draft: {current_story}
    Critique: {critique}

    Your task is to analyze the critique.
    - IF the critique is EXACTLY "APPROVED", you MUST stop revising and end the loop.
    - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.""",
    output_key="current_story",
)

# The loop terminator: this is reached only when the critic approves the story.
exit_loop_node = FunctionNode(
    func=exit_loop,
    name="ExitLoopNode",
)


def critic_route_decision(ctx):
    """Translate the critic's text output into a Workflow route."""
    critique = str(ctx.state.get("critique", "")).strip()
    route = "APPROVED" if critique == "APPROVED" else "REVISE"
    return Event(output=critique, route=route)


critic_router = FunctionNode(
    func=critic_route_decision,
    name="CriticRouteRouter",
)

# Workflow graph version of the original loop-agent pattern.
# The critic LLM stays the same; the router converts its text to a route value.
story_workflow = Workflow(
    name="StoryRefinementWorkflow",
    description="Write a story, critique it, refine it, and loop until the critic emits APPROVED.",
    edges=[
        (START, initial_writer_agent),
        (initial_writer_agent, critic_agent),
        (critic_agent, critic_router),
        (critic_router, {"APPROVED": exit_loop_node, "REVISE": refiner_agent}),
        (refiner_agent, critic_agent),
    ],
)

runner = InMemoryRunner(node=story_workflow)


async def main():
    response = await runner.run_debug(
        "Write a short story about a lighthouse keeper who discovers a mysterious, glowing map"
    )
    return response


if __name__ == "__main__":
    asyncio.run(main())
