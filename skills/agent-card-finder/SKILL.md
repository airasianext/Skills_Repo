---
name: agent-card-finder
description: Expert skill for locating, deriving, and displaying Gemini Enterprise and Cloud Run agent card configurations. Helps developers extract and audit the technical definitions of deployed agents.
---

# Agent Card Finder Skill

A specialized skill for extracting, parsing, and verifying Agent-to-Agent (A2A) Agent Card JSON definitions for both Gemini Enterprise (Registered) and Cloud Run (Live Deployed) environments.

## Capabilities
- **Registered Card Retrieval:** Queries Gemini Enterprise Discovery Engine APIs to get currently registered agent definitions and parses out the stringified `a2aAgentDefinition.jsonAgentCard` into readable JSON.
- **Live Deployed Card Retrieval:** Fetches live schemas directly from deployed specialists via Cloud Run URLs (e.g., standard `.well-known/agent-card.json` endpoints).
- **Auto-Discovery & Mapping:** Scans local workspace metadata (`conductor/deploy_metadata/` and `GEMINI_ENTERPRISE_ENGINES.MD`) to resolve specialist names, Agent IDs, and Engine IDs automatically.
- **Compliance & Schema Verification:** Performs structural audits against standard A2A Pydantic validation specs (absolute URLs, required skill fields: id, name, description, tags, etc.).

## Workflow

### 1. Research & Resolution Phase
To retrieve an agent card, first resolve the mapping between the human-friendly specialist name (e.g., `Gonzalo`, `Edouard`, `Bertha`), the `Agent Resource ID` (GCP), and the `Engine ID` (GCP).

*   **Option A: Scan Metadata Files (Primary)**
    Check files in `conductor/deploy_metadata/*_ge_registration.MD` to read the exact mapping.
    *Example:* `gonzalo_ge_registration.MD` maps the specialist `Gonzalo` to:
    *   **Internal ID / Agent ID**: `gonzalo_your_personalization_expert`
    *   **Cloud Run Service Name**: `gonzalo-specialist`
    *   **GE App (Engine)**: `gemini-ent-prd-all-users_1765161671583`
    *   **Agent Resource ID**: `9572361076007788743`
    *   **Agent Card URL**: `https://blue---gonzalo-specialist-145252659490.us-central1.run.app/a2a/gonzalo_your_personalization_expert/.well-known/agent-card.json`

*   **Option B: Scan Engines Registry**
    Use `GEMINI_ENTERPRISE_ENGINES.MD` to map project environments to Discovery Engine App/Engine IDs.
    *   `next-gemini-ent-prd` default engine: `gemini-ent-prd-all-users_1765161671583`
    *   `next-gemini-ent-dev` default engine: `next-gemini-dev_1764553747829`

### 2. Retrieval Phase

#### Mode A: Registered Card (From Gemini Enterprise APIs)
To fetch the agent definition registered in Gemini Enterprise:
1.  Navigate to the `a2a_mono_repo/a2a_mono_repo_adk_a2ui/` directory.
2.  Retrieve using the `just` utility command:
    ```bash
    just ge-agent-get [project_id] [engine_id] [agent_resource_id]
    ```
    *Or directly execute the python script:*
    ```bash
    uv run python3 scripts/ge/get_agent.py --project [project_id] --engine [engine_id] --agent [agent_resource_id]
    ```
3.  Locate `a2aAgentDefinition.jsonAgentCard` in the API output. Since it is returned as a JSON-encoded string, extract and parse it into a pretty-printed JSON block.

#### Mode B: Live Card (Direct HTTP Call to Deployed Cloud Run)
To fetch the latest schemas directly from Cloud Run:
1.  Formulate the endpoint URL from metadata or construct a standard tagged format:
    `https://blue---[service-name]-145252659490.us-central1.run.app/a2a/[internal_id]/.well-known/agent-card.json`
2.  If the endpoint requires authentication (e.g., returning `403 Forbidden` or `401 Unauthorized` under Cloud Run IAM protection), fetch a Google OIDC ID token to authenticate the request:
    *   **Audience Resolution**: Extract the root URL of the service (everything before the `/a2a/` path). For example:
        `https://jsm-assistant-145252659490.us-central1.run.app` or `https://blue---rewards-specialist-145252659490.us-central1.run.app`
    *   **Token Generation**: Run the following shell command to generate an OIDC ID token for the target audience:
        ```bash
        gcloud auth print-identity-token --audiences=[TARGET_AUDIENCE]
        ```
    *   **Fetch with Header**: Execute a curl request or a python script passing the generated token inside the `Authorization` header:
        ```bash
        curl -H "Authorization: Bearer <IDENTITY_TOKEN>" "https://[CARD_URL]"
        ```
3.  Format and display the JSON card.

### 3. Verification Phase (Compliance Check)
Once the card is retrieved, inspect the JSON against standard A2A schema compliance guidelines:
-   **Absolute URLs**: Ensure `"url"` is an absolute path starting with `http://` or `https://` (relative URLs fail client-side).
-   **Skills Structure**: Every element inside the `"skills"` array MUST contain:
    -   `id` (string)
    -   `name` (string)
    -   `description` (string)
    -   `tags` (list of strings)
-   **Input/Output Modes**: Check presence of `defaultInputModes` and `defaultOutputModes` (e.g. `["text/plain"]`).

## Quick Reference Commands

| Goal | Command |
| :--- | :--- |
| List All Registered Agents | `just ge-agents-list <project> <engine_id>` |
| Get Registered Agent Config | `just ge-agent-get <project> <engine_id> <agent_resource_id>` |
| Update Agent Card JSON | `just ge-agent-card-update <project> <engine_id> <agent_resource_id> <card_url>` |

## Trigger Sentences
This skill should trigger on requests like:
- "find agent card"
- "get agent card json for Gonzalo"
- "derive agent card for project next-gemini-ent-prd"
- "show me the registered card for Edouard"
- "verify the agent card JSON for Bertha"
