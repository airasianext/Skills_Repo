---
name: adk-evaluation-hardener
description: Expert skill for configuring offline, crash-resistant, and high-performance Google ADK automated evaluations with togglable mock/live runs, evaluation topologies, and multi-tier data bootstrapping.
---

# ADK Evaluation Hardener Skill

This skill provides comprehensive procedural guidance on how to configure, secure, and bootstrap automated evaluations using the Google ADK (Agent Development Kit) in multi-agent architectures.

## Trigger Scenarios
Activate this skill when the user requests to:
*   "harden adk evaluations", "write evaluation tests", "add evaluation benchmarks"
*   "mock downstream agents", "intercept remote workflows"
*   "prevent evaluation timeouts or hangs"
*   "bootstrap evaluation data", "generate synthetic test cases"
*   "set up routing-only metrics or scorecards"
*   "optimize evaluation speed", "batch evaluation metrics"

## Available Resources
The following production templates are available in this skill directory for instant reference and reuse:
*   📁 **`run_eval_template.py`**: A fully-commented, complete boilerplate implementing global HTTPX socket timeouts, compliant NoneType crash-safeguards, dynamic subagent mocking interceptors, and custom scorecard reporting.
*   📁 **`split_dataset_template.py`**: A reusable CLI utility script to dynamically slice large golden JSON datasets into low-pressure, safe, sequential chunks.
*   📁 **`user_simulator_template.py`**: A programmatic script demonstrating how to spin up the ADK's native UserSimulator with ConversationScenarios to dynamically generate and record high-fidelity golden traces from scratch.
*   📁 **`topology_isolated_template.py`**: Reference template implementing Option 1 (standard native isolated per-turn evaluation pattern).
*   📁 **`topology_batched_cot_template.py`**: Reference template implementing Option 2 (custom evaluator demonstrating consolidated trajectory batching using Pydantic Structured JSON schemas and turn-by-turn Chain of Thought reasoning).

---

## 1. Core Architectural Pillars

### A. Evaluation Topology: Isolated vs. Consolidated (Batched)
When architecting your evaluation harness, allow developers to choose the evaluation topology that fits their budget, latency, and context requirements:

**Option 1: Isolated Per-Turn Evaluation (Native ADK Default)**
*   **How it works**: The LLM Judge evaluates each turn in a silo via separate API calls.
*   **Pros**: Extreme clinical precision (zero attention dilution).
*   **Cons**: High API cost, slow execution (prone to rate limits), and blind to conversational context (e.g., struggles if user intent relies on history 3 turns ago).
*   **When to use**: Strict compliance testing where a single turn's literal output must be flagged regardless of context. (See `topology_isolated_template.py` for reference boilerplate).

**Option 2: Consolidated Trajectory Evaluation (Batched with CoT)**
*   **How it works**: The entire conversation transcript is passed to the judge in a *single prompt*. To prevent the judge from "smoothing over" mistakes in long contexts, you force the judge to evaluate turn-by-turn using **Structured Outputs** and mandatory **Chain of Thought (CoT)**.
*   **Pros**: ~85%+ reduction in API calls/cost, full conversational context (understands long workflows), ultra-fast execution.
*   **Implementation Strategy**: Create a custom ADK `Evaluator` class that passes the full trace to `gemini-3-flash-preview` using this JSON Schema constraint (See `topology_batched_cot_template.py` for Pydantic schema implementation):
    ```json
    {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "turn_number": { "type": "integer" },
          "clinical_rationale": { "type": "string", "description": "Mandatory CoT reasoning before scoring" },
          "routing_score": { "type": "number", "minimum": 0, "maximum": 1 }
        },
        "required": ["turn_number", "clinical_rationale", "routing_score"]
      }
    }
    ```
    *Note: The mandatory `clinical_rationale` forces the LLM's attention mechanism to focus deeply on that specific turn before scoring it, mitigating the "lost-in-the-middle" effect.*

### B. Dynamic Mock vs. Live Execution Toggle
Always provide a dynamic switch (typically using an environment variable like `MOCK_REMOTE_A2A`) within your `patched_run_async_impl` monkeypatch. This enables developers to run fast, local, offline sandbox tests, or E2E staging integration tests against live Google Cloud APIs:

```python
try:
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from google.adk import Event
    from google.genai import types as genai_types

    _orig_run_async_impl = RemoteA2aAgent._run_async_impl

    async def patched_run_async_impl(self, ctx):
        # 1. READ ENVIRONMENT TOGGLE (Default to Mocking)
        if os.getenv("MOCK_REMOTE_A2A", "true").lower() != "true":
            async for event in _orig_run_async_impl(self, ctx):
                yield event
            return

        # 2. LOCAL SANDBOX MOCK RESPONSES
        name = self.name.lower()
        print(f"\n🎯 [MOCK INTERCEPT] Intercepted remote call to downstream '{self.name}'!")
        
        # Inject realistic dummy outputs based on the agent requested...
        msg = f"Mock successful execution for {self.name}."
            
        yield Event(
            author=self.name,
            content=genai_types.Content(role="model", parts=[genai_types.Part(text=msg)]),
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
        )

    RemoteA2aAgent._run_async_impl = patched_run_async_impl
except Exception as e:
    pass
```

### C. Socket Timeout Protection (Urllib3, HTTPX)
Always override sync and async client initializers to force strict timeouts. This guarantees that Vertex AI or OAuth socket drops cannot hang the event loop indefinitely.

### D. Compliant NoneType Inferences Safeguards
If a model generation fails, the ADK `LocalEvalService` receives `None` instead of an inference list, which crashes the suite with a `TypeError`. Always patch `LocalEvalService._evaluate_single_inference_result` to dynamically backfill a Pydantic-compliant `Invocation` array matching the original conversation length with `[Inference Failed]` payloads.

### E. Selective Metric Failures (Routing Only)
When testing a root agent's routing quality, response mismatch or hallucination errors should not cause a pipeline test crash. Intercept `AgentEvaluator._process_metrics_and_get_failures` to display all scores on stdout, but **only append to the failures list if a routing/tool_use metric fails**.

---

## 2. Bootstrapping Evaluation Data

In scenarios where the team does not have a robust production dataset, employ this three-tiered progressive bootstrapping strategy:

```
                  ┌──────────────────────────────┐
                  │ Tier 3: LLM Synthetic Slices  │  <── Scaling to 50+ cases
                  └──────────────┬───────────────┘
                                 │
                  ┌──────────────┴───────────────┐
                  │ Tier 2: ADK User Simulator   │  <── Expanding to 20+ cases
                  └──────────────┬───────────────┘
                                 │
                  ┌──────────────┴───────────────┐
                  │  Tier 1: Interactive UI Seed  │  <── Start with 3-5 cases
                  └──────────────────────────────┘
```

### Tier 1: Interactive UI Seed (3-5 Cases)
*   **Method**: Launch the local ADK Web UI. Manually conduct 3 to 5 basic representative flows.
*   **Result**: Export the golden traces as a baseline JSON seed file.

### Tier 2: ADK User Simulator (20+ Cases)
Avoid writing manual turns by defining lightweight **Personae and Goals** in a `ConversationScenario` block:
```json
{
  "eval_id": "scenario-001",
  "conversation_scenario": {
    "user_persona": "An aggressive customer who demands baggage check.",
    "user_goal": "Confirm baggage status and refuse any upselling."
  }
}
```
Run the ADK evaluator. The LLM-based `UserSimulator` will talk to your agent dynamically and automatically record the golden traces. (See `user_simulator_template.py`).

### Tier 3: LLM-Driven Synthetic Generation (50+ Cases)
Use an offline LLM prompt to synthetically generate diverse conversation traces. Prompt Blueprint:
```text
Generate 20 user conversation traces for an airline concierge chatbot.
Include a mix of successful routings, unprocessable escalations, and out-of-scope inquiries.
Output the results strictly in valid ADK JSON EvalCase schema.
```

---

## 3. Operational Best Practices & Quota Safeguards

1.  **Keep Chunks Small**: Always partition large evaluation datasets into chunks of **10 to 12 cases** (e.g. using `split_dataset_template.py`) to bypass Vertex AI rate limit throttling (HTTP 429).
2.  **Sequential Execution**: Run individual parts sequentially rather than concurrently to prevent rate-limit overlapping blocks.
3.  **Global Socket Timeouts**: Enforce default 60-second read and 30-second connect timeout on `httpx` synchronous and asynchronous clients inside the test runner.
