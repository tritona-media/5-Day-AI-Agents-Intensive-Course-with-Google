# Day 3 - Context Engineering: Sessions & Memory

## Agent with In-Memory Session

The runner is given an instance of `InMemorySessionService`, which stores session data temporarily in memory. A session is created manually outside the runner through the session service. When calling `runner.run_async`, pass both the user ID and the session ID; the runner uses the session service to find the corresponding session. If the runner cannot find that session ID, it raises an error rather than creating a new session automatically.

One user can have multiple sessions, so each run must identify both the user and the specific session. A session contains the conversation history as events in chronological order. In the example, the agent remembers the user's name from an earlier exchange because the next turn uses the same session ID.

## Agent Experiment

If you use a different session ID for each user prompt, the agent forgets your name between prompts. This demonstrates that the agent can remember information only within a session.