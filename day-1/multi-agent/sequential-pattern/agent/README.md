# Sequential Architecture Pattern

## Original Agent
[source file](./agent.py)

A sequential agent is created using the `google.adk.agents.SequentialAgent` class. It contains a `sub_agents` list, and each agent in that list runs in a fixed order. The output of one agent becomes the input for the next, and the final result is returned by the sequential agent.

This pattern is useful when a deterministic execution order is required, especially when each step depends on the previous step's output or when the workflow must follow a strict sequence.

## Agent Experiments
[source file](./agent_experiment.py)

The `google.adk.agents.SequentialAgent` class is marked as deprecated. A newer approach is to model the flow as a graph of nodes and edges, similar to LangGraph, using the `google.adk.workflow.Workflow` class and its `edges` property.

The `edges` property accepts a list of tuples that define the connections between agent nodes. In this example, the workflow follows a strict linear sequence:

`START -> outline_agent -> writer_agent -> editor_agent`

This keeps the same execution order while making the pattern more flexible and aligned with modern graph-based workflow designs.