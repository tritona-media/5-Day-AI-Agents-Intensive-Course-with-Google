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
