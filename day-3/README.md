# Day 3 - Context Engineering: Sessions & Memory

## Agent with In-Memory Session

The runner is given an instance of `InMemorySessionService`, which stores session data temporarily in memory. A session is created manually outside the runner through the session service. When calling `runner.run_async`, pass both the user ID and the session ID; the runner uses the session service to find the corresponding session. If the runner cannot find that session ID, it raises an error rather than creating a new session automatically.

One user can have multiple sessions, so each run must identify both the user and the specific session. A session contains the conversation history as events in chronological order. In the example, the agent remembers the user's name from an earlier exchange because the next turn uses the same session ID.

## Agent with In-Memory Session - Experiment

If you use a different session ID for each user prompt, the agent forgets your name between prompts. This demonstrates that the agent can remember information only within a session.

## Agent with Persistent Session

The persistent-session example uses a local SQLite database to save session data between runs. Unlike an in-memory session, this data remains available after the runner exits. The database can be opened with a SQLite viewer to inspect its tables, including the stream of events recorded for a session.

When the runner is restarted with the same database URL and session ID (and the same app and user IDs), it can retrieve the saved conversation history. The agent can then use information from earlier turns—for example, facts the user shared in a previous run—to respond in the new run.

The event stream belongs to a specific session, so separate session IDs have isolated histories. If you start another session with a different ID, its event stream does not include the earlier conversation, and the agent will not know your name until you tell it again. This demonstrates that sessions are isolated from one another.

## Agent with Context Compaction

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