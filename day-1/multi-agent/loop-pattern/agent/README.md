# Loop Agent Architecture Pattern

## Original Agent
[source file](./agent.py)

A loop agent repeatedly invokes the same sub-agents until a specific condition is met. This pattern is useful when an initial output needs iterative improvement through feedback and revision.

In this example, an initial writer agent creates the first draft of a story. The loop agent then passes that draft to a critic agent, which provides feedback on what could be improved. The draft and the critique are sent to a refiner agent, which rewrites the story. This revised version is sent back to the critic agent, which evaluates it again until the result is approved. The refiner agent ultimately ends the loop by calling a designated tool function.

A sequential agent is also required because the initial writer agent must create the first draft before the loop agent takes over.

![Loop Agent Architecture](./assets/loop-architecture.svg)

## Agent Experiments
[source file](./agent_experiment.py)

This experiment rewrites the original loop using the `google.adk.workflow.Workflow` class instead of `google.adk.agents.LoopAgent`, with the behavior expressed as a graph of connected nodes.

One of the key takeaways is that workflow nodes can be either agent nodes or function nodes. In this pattern, the initial writer still creates the first draft, the critic still evaluates it, and the refiner still improves it. The difference is that the decision to keep looping or exit the loop is handled by a function node that emits a route value.

The critic agent produces the critique text, and a small function-node router converts that output into a route. If the route is `APPROVED`, the workflow follows the exit branch. If the route is `REVISE`, it follows the branch back to the refiner. In other words, the loop is controlled by graph edges rather than by the fixed `LoopAgent` sequence itself.

This is the main conceptual shift: instead of a loop agent deciding when to continue, the workflow graph decides based on routing. The exit function returns a `google.adk.events.event.Event` object with `route="APPROVED"`, while the revise branch sends the flow back to the refiner agent.