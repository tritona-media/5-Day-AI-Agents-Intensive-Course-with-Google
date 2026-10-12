# Day 3 - Context Engineering: Sessions & Memory

## Agent with In-Memory Session

Source: [agent.py](./agent-sessions/agent/agent.py)

The runner is given an instance of `InMemorySessionService`, which stores session data temporarily in memory. A session is created manually outside the runner through the session service. When calling `runner.run_async`, pass both the user ID and the session ID; the runner uses the session service to find the corresponding session. If the runner cannot find that session ID, it raises an error rather than creating a new session automatically.

One user can have multiple sessions, so each run must identify both the user and the specific session. A session contains the conversation history as events in chronological order. In the example, the agent remembers the user's name from an earlier exchange because the next turn uses the same session ID.

## Agent with In-Memory Session - Experiment

Source: [agent_experiment.py](./agent-sessions/agent/agent_experiment.py)

If you use a different session ID for each user prompt, the agent forgets your name between prompts. This demonstrates that the agent can remember information only within a session.

## Agent with Persistent Session

Source: [agent.py](./agent-persistent-sessions/agent/agent.py)

The persistent-session example uses a local SQLite database to save session data between runs. Unlike an in-memory session, this data remains available after the runner exits. The database can be opened with a SQLite viewer to inspect its tables, including the stream of events recorded for a session.

When the runner is restarted with the same database URL and session ID (and the same app and user IDs), it can retrieve the saved conversation history. The agent can then use information from earlier turns—for example, facts the user shared in a previous run—to respond in the new run.

The event stream belongs to a specific session, so separate session IDs have isolated histories. If you start another session with a different ID, its event stream does not include the earlier conversation, and the agent will not know your name until you tell it again. This demonstrates that sessions are isolated from one another.

## Agent with Context Compaction

Source: [agent.py](./agent-context-compaction/agent/agent.py)

Long conversations can exceed the amount of history that is practical to send
to a model on every turn. ADK event compaction addresses this by summarizing
older invocations and using those summaries when it builds the model's context.

In this example, `compaction_interval=3` triggers compaction after three new
user-initiated invocations have completed. An invocation includes the user's
message and the events produced while the agent responds, such as its answer
and any tool activity. Compaction therefore summarizes conversation activity
from both sides; it does not summarize only the model's answers.

`overlap_size=1` includes one invocation immediately before the first new
invocation in the next compaction window. For example:

| Compaction | New invocations since the previous compaction | Window summarized |
| --- | --- | --- |
| First | 1–3 | 1–3 |
| Second | 4–6 | 3–6 |
| Third | 7–9 | 6–9 |

The repeated invocation provides continuity between adjacent summaries. For
example, if invocation 3 introduces a topic and later invocations discuss it,
including invocation 3 in the next window gives the summarizer that context.
This can help preserve the connection, though it is a trade-off: the overlapping
information may appear in more than one summary and use some additional context.

Compaction does not delete the original events from the persisted session
history. When ADK assembles the next model request, it uses the valid
compaction summaries in place of raw events covered by their time ranges, while
leaving events outside those ranges available as raw history. Partially
overlapping summaries can both remain in the model context; ADK does not
automatically merge every new summary into one ever-growing summary. As a
result, this setting reduces the raw history sent to the model, but does not
guarantee that the number of summaries—or total context—stays constant.

ADK creates summaries with an event summarizer. If no summarizer is explicitly
configured, ADK can use an LLM summarizer based on the agent's model. In this
example, that means an additional Gemini model request may be made for
compaction, in addition to the normal response request. That request is billed
according to the configured provider, credentials, and project/account; it is
not a local, cost-free operation.

## Agent with Context Caching

The system prompt is included in the model request on every turn. For a long
system prompt that stays the same across turns, the inference provider may be
able to reuse the computation it has already done for that prompt instead of
processing the same prefix from scratch. This is context caching. It can reduce
the repeated work (and, depending on the provider, cost or latency), but the
prompt still needs to be part of each request.

You can check whether caching is being used by inspecting the model response
metadata. Providers may report cache-related fields such as the number of
tokens read from cache or a cached-content identifier. The field names and
meaning vary by provider, so consult the metadata returned by the model and the
provider's documentation rather than assuming that caching occurred.

Whether caching must be enabled manually depends on the inference provider and
the kind of caching it offers. Some providers automatically cache eligible
repeated prompt prefixes; others require explicitly creating or referencing a
cached prompt. Check the provider's rules for eligibility, minimum prompt size,
cache lifetime, and billing, and verify the response metadata to confirm that
the request actually used the cache.

## Agent with Session State

Source: [agent.py](./agent-session-state/agent/agent.py)

The event history records the conversation and tool activity. Session state is
a structured key-value store for information an agent or its tools need to
access directly, such as a user's name or the current step of a workflow. It
complements the event history rather than replacing it.

A tool can read or update state through the `tool_context` parameter ADK
provides when it calls the tool. In the example, `save_userinfo` writes the
user's name and country to `tool_context.state`, and `retrieve_userinfo` reads
them back on a later turn. ADK tracks these updates through its event handling,
so tools should use `tool_context.state` rather than directly modifying a
`Session` object's state outside an agent invocation.

Use a scope prefix followed by a colon when a key is temporary, user-scoped,
or app-scoped: `temp:key` is limited to the current invocation, `user:key` is
shared across sessions for the same user, and `app:key` is shared across users
and sessions in the same app. Keys without a prefix, such as `current_step`,
belong to the current session. State persistence also depends on the session
service; this example uses `InMemorySessionService`, so the values are lost
when the process ends.

## Agent with Memory

Source: [agent.py](./agent-memory-workflow/agent/agent.py)

An agent can have both a short-term and a long-term memory. The short-term memory is the active session: it stores the current conversation history and the recent events that belong to a specific session ID. This is useful for continuity within one chat thread, but it is isolated per session.

The long-term memory is a shared memory store that lives outside any single session. It is intended for important facts about the user that should persist across conversations, such as preferences, personal details, or recurring context. In this example, the memory service is created with `InMemoryMemoryService()`, so it is still in-memory for local testing, but it is shared across all sessions for the same app.

The important part is that facts do not automatically move from the current session into the long-term memory. The transfer must be manually triggered with `memory_service.add_session_to_memory(session)`. This lets the developer decide which session events should become durable memory. Once added, those facts can be reused in future sessions.

Only the agent can access the long-term memory through the predefined `load_memory` tool. This means the model decides on each turn whether it needs to look up prior context data before answering. The memory lookup is selective and on-demand, rather than always injected into the prompt.

A different pattern is `preload_memory`, which loads all available memory into the context for every turn. That is useful when you want the model to always see the long-term facts, but it can add more context and increase prompt size. In contrast, `load_memory` gives the agent a more targeted, decision-based approach.

In the example, the agent is initialized with `tools=[load_memory]`, so it can decide when it needs to recall earlier information. For example, after the first session records that the user likes a certain color or has a birthday, the developer explicitly adds that session to memory and then opens a different session; the agent can answer questions using the stored long-term facts without needing the earlier conversation to still be active.

## Agent with Automated Memory

Source: [agent.py](./agent-automated-memory/agent/agent.py)

Automated memory is a way to keep the long-term memory store updated without manually calling the memory service in each script. Instead of writing a custom step after every turn, the agent can register a callback hook that runs automatically as part of the agent lifecycle.

In this example, the agent defines an `after_agent_callback` named `auto_save_to_memory`. That hook runs after the agent finishes processing a turn and then calls:

```python
await callback_context._invocation_context.memory_service.add_session_to_memory(
    callback_context._invocation_context.session
)
```

This means the current session is automatically written into the shared memory service at the end of each turn. The effect is that useful facts are retained without the developer needing to remember to call `memory_service.add_session_to_memory(session)` manually after every interaction.

The agent also attaches `preload_memory` to its tools list. With that configuration, the model receives the long-term memory context on every turn, so it can answer from previously stored facts even when the new prompt happens in a different session. This is useful for cross-session continuity, but it also means the prompt becomes larger because long-term memory is loaded each time.

ADK exposes several callback hooks that can be plugged into an agent lifecycle. Common examples include:

- `before_agent_callback`: runs before the agent begins work
- `after_agent_callback`: runs after the agent completes the turn
- `before_model_callback`: runs before the model request is sent
- `after_model_callback`: runs after the model responds
- `before_tool_callback`: runs before a tool is invoked
- `after_tool_callback`: runs after a tool finishes

These hooks are useful for monitoring, enrichment, validation, or automatic persistence. In the automated memory example, the `after_agent_callback` is the key hook because it turns a normal conversation step into a memory-saving event without explicit application code after every run.

The result is a simple pattern: the agent responds, the hook saves the conversation into memory, and future sessions can use that memory to answer questions with context that was previously gathered in another chat.
