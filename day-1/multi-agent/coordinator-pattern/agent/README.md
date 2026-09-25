# Coordinator Architecture Pattern

## Original Agent
[source file](./agent.py)

### Explanation

In this pattern, a coordinator agent decides which specialized agent to route the task to based on the user prompt, context, intermediate results, and its instructions.

For example, a coordinator may choose between a writer, coder, or research agent depending on the request.

![Coordinator architecture](./assets/coordinator-architecture.svg)

If the user prompt is `"Research NVIDIA's latest financial results and write a report."` the coordinator may first route the task to a research agent and then to a writer agent.

If the user prompt is `"Fix this Python code and explain the changes,"` it will likely route the request to a coder agent first, followed by a writer agent.

There is no fixed execution path. The order of operations is determined dynamically by the coordinator agent.

Even when the coordinator is given strong instructions to prefer a certain sequence, that behavior is not guaranteed. It acts more like a bias toward a workflow than an enforced deterministic process.

### Agent State

Agents share the same session state. Each agent can write its output into the session state under a self-defined key, such as `research_findings`. That value can then be injected into another agent's instructions using `{<state_key>}`.

## Agent Experiments
[source file](./agent_experiment.py)

I created a coordinator agent that orchestrates two specialized agents:
* `PythonCodeAgent`
* `PythonCodeReviewAgent`

The coordinator is instructed to first generate Python code based on the user's request, then pass that output to the review agent for refinement. The final result is produced by combining both stages.

The coding agent writes its output to a session-state key, and that value is injected into the review agent's instruction prompt.

I found that a clear pattern for an agent instruction prompt is:
```
Role:
...

Goal:
...

Task:
1. ...
2. ...
```

In the Task section, you define the steps the agent should take to achieve its goal.