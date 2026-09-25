# Sequential Architecture Pattern

## Original Agent
[source file](./agent.py)

A sequential agent is created using the `google.adk.agents.SequentialAgent` class. It contains a `sub_agents` list, and each agent in that list runs in a fixed order. The output of one agent becomes the input for the next, and the final result is returned by the sequential agent.

This pattern is useful when a deterministic execution order is required, especially when each step depends on the previous step's output or when the workflow must follow a strict sequence.