# Day 2 - Agent Tools & Interoperability with Model Context Protocol (MCP)

## Agent Custom Tools v1

In this example, the currency agent is equipped with two tool functions: `get_fee_for_payment_method()` and `get_exchange_rate()`.

Each tool returns a dictionary containing a `status` key, along with either a result field or an error field, depending on the outcome of the operation.

The agent's instructions clearly define when each tool should be used. From there, the agent decides which function to call and which arguments to pass in order to complete the task effectively.

The tool functions should include a clear docstring that explains what they do, what they return, and their parameters in detail. Including a few examples also helps the agent understand them more clearly.

## Agent Custom Tools v2

In the first version of the agent, the language model handled the final calculation. This is not ideal because LMs are not reliable at arithmetic. They are probabilistic systems that predict the next likely token rather than perform precise computation.

A better approach is to delegate the calculation to a tool. In many agent systems, this is done by having the model generate Python code that runs in a sandboxed environment for the math. This is also the general approach used by systems such as Gemini and ChatGPT.

For this version, the agent is instructed to generate Python code only. That code is then executed in a sandbox environment, allowing the model to reason about the task while the actual calculation is performed by a reliable runtime.

The `enhanced_currency_agent` acts as an orchestrator. It first calls the tool functions to retrieve the fee percentage and exchange rate, then builds a prompt for the `CalculationAgent` to generate Python code. That code is executed in a sandbox, and the orchestrator uses the result to produce the final summary.

Every result from the tool calls and sub-agent calls is added to the context of the `enhanced_currency_agent`. With this information collected in one place, it can assemble a clear final summary.

## Agent MCP Tools

`google.adk.tools.mcp_tool.mcp_toolset.McpToolset` configures a connection between an agent and an MCP server, and exposes the server's tools to the agent. In this example, the server is the local npm package `@modelcontextprotocol/server-everything`, launched with `npx`. This development server provides many tools for testing MCP clients; we filter its tool list to just `getTinyImage` for this example.

MCP servers can communicate over three methods:

| Method | When to use it |
| --- | --- |
| stdio | The MCP server runs as a local child process and communicates over standard input and output. Use this for local tools and development. |
| SSE | Server-to-client only: the server streams events to the client, while client requests use a separate channel. Use this for remote servers that use the SSE transport. |
| Streaming HTTP | Bidirectional: client and server can both send messages over the HTTP connection. Use this for remote servers using the newer Streamable HTTP transport. |

We use `stdio` because `npx` launches the MCP server locally. The `McpToolset` is included in the agent's `tools` list, and the agent receives the prompt `Provide a sample tiny image`; it can call `getTinyImage` to generate the image.

## Agent MCP Tools - Experiments
The experiment sets up an MCP tool that fetches content from a URL and provides it to an agent. The agent uses the tool to retrieve the URL's content, then summarizes it concisely.

## Agent Human-In-The-Loop (Web)

The shipping coordinator is an ADK app built around an `LlmAgent`, with resumability enabled so the interaction can pause while a human reviews a request and continue after a decision is submitted. The agent has a `place_shipping_order` tool that receives a `ToolContext`, which carries the human-in-the-loop confirmation state. Small orders are approved automatically; for larger orders, the tool requests confirmation and returns a pending-status dictionary. When the app resumes, the tool reads the confirmation from the context and returns a dictionary indicating whether the order was approved or rejected.

## Agent Human-In-The-Loop (CLI)

This command-line example demonstrates human approval using ADK concepts including sessions, runners, and events. The program creates a session, runs the agent, inspects its events for an approval request, and then resumes the same invocation with the human decision. Run the workflow from a Python shell; it prints the agent responses and approval outcome in the terminal.

## Agent Human-In-The-Loop (CLI) - Experiment

This experiment demonstrates how to add a human-in-the-loop approval step to an agent. The agent is given a custom `generate_images` function, not the MCP tool itself. The custom function requests confirmation through `ToolContext`; the ADK emits a separate confirmation-request event for the client to present to the user. The client sends its decision as a `FunctionResponse` matched to that request by its function-call ID, then resumes the same invocation using its invocation ID. If the user approves, the custom function calls the MCP tool and returns its result. The `pending` status returned while waiting is application-defined; it is not the ADK confirmation protocol.
