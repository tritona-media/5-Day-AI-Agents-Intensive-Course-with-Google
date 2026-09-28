# Day 2 - Agent Tools & Interoperability with Model Context Protocol (MCP)

## Agent v1

In this example, the currency agent is equipped with two tool functions: `get_fee_for_payment_method()` and `get_exchange_rate()`.

Each tool returns a dictionary containing a `status` key, along with either a result field or an error field, depending on the outcome of the operation.

The agent's instructions clearly define when each tool should be used. From there, the agent decides which function to call and which arguments to pass in order to complete the task effectively.

The tool functions should include a clear docstring that explains what they do, what they return, and their parameters in detail. Including a few examples also helps the agent understand them more clearly.

## Agent v2

In the first version of the agent, the language model handled the final calculation. This is not ideal because LMs are not reliable at arithmetic. They are probabilistic systems that predict the next likely token rather than perform precise computation.

A better approach is to delegate the calculation to a tool. In many agent systems, this is done by having the model generate Python code that runs in a sandboxed environment for the math. This is also the general approach used by systems such as Gemini and ChatGPT.

For this version, the agent is instructed to generate Python code only. That code is then executed in a sandbox environment, allowing the model to reason about the task while the actual calculation is performed by a reliable runtime.

The `enhanced_currency_agent` acts as an orchestrator. It first calls the tool functions to retrieve the fee percentage and exchange rate, then builds a prompt for the `CalculationAgent` to generate Python code. That code is executed in a sandbox, and the orchestrator uses the result to produce the final summary.

Every result from the tool calls and sub-agent calls is added to the context of the `enhanced_currency_agent`. With this information collected in one place, it can assemble a clear final summary.