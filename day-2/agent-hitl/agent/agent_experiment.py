import asyncio
import base64
import uuid

from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from dotenv import load_dotenv
from dotenv import load_dotenv
from IPython.display import display, Image as IPImage
from IPython.display import display, Image as IPImage

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# MCP integration with Everything Server
mcp_image_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-everything",
            ],
            tool_filter=["getTinyImage"],
        ),
        timeout=30,
    )
)


async def generate_images(count: int, tool_context: ToolContext) -> dict:
    """Generate images, requesting approval before generating more than one."""
    if count < 1:
        return {"status": "error", "message": "count must be at least 1"}

    if count > 1:
        confirmation = tool_context.tool_confirmation
        if confirmation is None:
            tool_context.request_confirmation(
                hint=f"May I generate {count} images?",
                payload={"count": count},
            )
            return {"status": "pending", "count": count}

        if not confirmation.confirmed:
            return {"status": "rejected", "count": count}

    tools = await mcp_image_server.get_tools()
    image_tool = next(
        (tool for tool in tools if tool.name == "get-tiny-image"),
        None,
    )
    if image_tool is None:
        raise RuntimeError("MCP tool 'get-tiny-image' was not found")

    images = []
    for _ in range(count):
        images.append(await image_tool.run_async(args={}, tool_context=tool_context))

    return {"status": "generated", "count": count, "images": images}


# Create image agent with MCP integration
image_agent = LlmAgent(
    model=Gemini(model="gemini-3.5-flash", retry_options=retry_config),
    name="image_agent",
    instruction=(
        "Generate images requested by the user by calling generate_images. "
        "Pass the number of images the user requested. Do not call any other "
        "image-generation tool. If image generation is rejected, respond with "
        "a message to the user indicating that image generation was rejected"
        "and provide an explanation."
    ),
    tools=[FunctionTool(func=generate_images)],
)

image_app = App(
    name="image_coordinator",
    root_agent=image_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

session_service = InMemorySessionService()


def find_images(value):
    """Yield MCP image content blocks nested in a tool result."""
    if isinstance(value, dict):
        if value.get("type") == "image" and isinstance(value.get("data"), str):
            yield value
            return
        for child in value.values():
            yield from find_images(child)
    elif isinstance(value, list):
        for child in value:
            yield from find_images(child)


def display_tool_images(events):
    for event in events:
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            function_response = part.function_response
            if function_response:
                for image in find_images(function_response.response):
                    display(IPImage(data=base64.b64decode(image["data"])))


def get_confirmation_request(events):
    for event in events:
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            function_call = part.function_call
            if function_call and function_call.name == "adk_request_confirmation":
                return function_call.id, event.invocation_id
    return None

def create_session(name: str, user_id: str, session_id: str):
    """Create a session for the given app name, user ID, and session ID."""
    return session_service.create_session(
        app_name=name,
        user_id=user_id,
        session_id=session_id,
    )


async def main():
    image_runner = Runner(
        app=image_app,  # Pass the app instead of the agent
        session_service=session_service,
    )

    user_id = "image_user"
    session_id = f"image_{uuid.uuid4().hex[:8]}"
    await create_session(name=image_app.name, user_id=user_id, session_id=session_id)

    try:
        prompt = input("How many images should I create? ")
        initial_events = []
        async for event in image_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=prompt)],
            ),
        ):
            print(f"#### Event: {event}")
            initial_events.append(event)

        approval = get_confirmation_request(initial_events)
        events = initial_events
        if approval:
            approved = input(
                "The agent wants to generate more than one image. Approve? [j/N] "
            ).strip().lower() in {"j", "ja", "y", "yes"}
            approval_id, invocation_id = approval
            confirmation_response = types.FunctionResponse(
                id=approval_id,
                name="adk_request_confirmation",
                response={"confirmed": approved},
            )
            events = []
            async for event in image_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(
                    role="user",
                    parts=[types.Part(function_response=confirmation_response)],
                ),
                invocation_id=invocation_id,
            ):
                print(f"####- Event: {event}")
                events.append(event)

        display_tool_images(events)
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
    finally:
        await mcp_image_server.close()

if __name__ == "__main__":
    asyncio.run(main())
