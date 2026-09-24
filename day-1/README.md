# Day 1 - Introduction to Agents

## Single Agent
See documentation [here](./single-agent/README.md)

## Multi Agent
See documentation [here](./multi-agent/README.md)

## Running the agent
There are several ways to run the agent:

* `python agent[_experiment].py`
* `adk run agent` (this starts a chat loop locally; type exit to exit)
* `adk web agent` (starts a local server with a chat UI)
* `adk deploy cloud_run --project=<project_id> --region=europe-west3 --with_ui agent -- --allow-unauthenticated` (this deploys the agent to Google Cloud and comes with a free chat UI; click on the URL that is generated)

## Google Cloud Console
This is the Google Cloud Console where you can manage your deployment, billing etc.: https://console.cloud.google.com/