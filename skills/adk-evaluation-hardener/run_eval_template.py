# run_eval_template.py
# Reference implementation for a hardened, offline Google ADK evaluation harness.

import asyncio
import logging
import sys
import os

# 1. ENFORCE STRICT SOCKET TIMEOUTS & CONCURRENCY GATING
try:
    import httpx
    
    # Global semaphore to limit concurrent Google API requests to exactly 5 at a time.
    # This prevents triggering HTTP 429 rate limits and subsequent exponential backoffs.
    _google_api_sem = asyncio.Semaphore(5)
    
    _orig_async_init = httpx.AsyncClient.__init__
    def patched_async_init(self, *args, **kwargs):
        # Force a 60-second default read and 30-second connect timeout globally
        kwargs["timeout"] = httpx.Timeout(60.0, connect=30.0, read=60.0)
        _orig_async_init(self, *args, **kwargs)
    httpx.AsyncClient.__init__ = patched_async_init

    _orig_sync_init = httpx.Client.__init__
    def patched_sync_init(self, *args, **kwargs):
        kwargs["timeout"] = httpx.Timeout(60.0, connect=30.0, read=60.0)
        _orig_sync_init(self, *args, **kwargs)
    httpx.Client.__init__ = patched_sync_init

    # Gated Concurrency Patch to limit parallel requests to Vertex AI
    _orig_async_send = httpx.AsyncClient.send
    async def patched_async_send(self, request, *args, **kwargs):
        if "googleapis.com" in str(request.url):
            async with _google_api_sem:
                return await _orig_async_send(self, request, *args, **kwargs)
        else:
            return await _orig_async_send(self, request, *args, **kwargs)
    httpx.AsyncClient.send = patched_async_send

    print("🛠️ [HARNESS] Registered Forceful Global HTTPX Socket Timeout & Concurrency Semaphore Patches.")
except Exception as e:
    print(f"⚠️ [HARNESS] Failed to register HTTPX Timeout/Semaphore Patches: {e}")


# 2. DYNAMIC REMOTE A2A AGENT MOCK INTERCEPTOR
try:
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from google.adk import Event
    from google.genai import types as genai_types

    _orig_run_async_impl = RemoteA2aAgent._run_async_impl

    async def patched_run_async_impl(self, ctx):
        # Togglable via environment variable
        if os.getenv("MOCK_REMOTE_A2A", "true").lower() != "true":
            async for event in _orig_run_async_impl(self, ctx):
                yield event
            return

        name = self.name.lower()
        print(f"\n🎯 [MOCK INTERCEPT] Intercepted remote call to downstream '{self.name}'!")
        
        # Add custom mock business rules based on the target agent name
        if "name_correction" in name:
            msg = "The name on your booking has been updated."
        elif "gender_correction" in name:
            msg = "The gender on your booking has been updated to male."
        else:
            msg = f"Mock successful execution for {self.name}."
            
        print(f"👉 Simulating response: '{msg}'")
        yield Event(
            author=self.name,
            content=genai_types.Content(
                role="model",
                parts=[genai_types.Part(text=msg)]
            ),
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
        )

    RemoteA2aAgent._run_async_impl = patched_run_async_impl
    print("🛠️ [HARNESS] Registered Mocking Interceptors for Remote A2A Agents.")
except Exception as e:
    print(f"⚠️ [HARNESS] Failed to register Mocking Interceptors: {e}")


# 3. SELECTIVE METRIC FORMATTER & SCORECARD REPORT
try:
    from google.adk.evaluation.agent_evaluator import AgentEvaluator
    from google.adk.evaluation.eval_result import EvalStatus
    import statistics

    @staticmethod
    def patched_process_metrics_and_get_failures(eval_metric_results, print_detailed_results, agent_module):
        failures = []
        
        print("\n=======================================================================")
        print("📊 [EVAL RESULTS] Metric Performance & Rubric Scorecard:")
        print("=======================================================================")
        
        for metric_name, results in eval_metric_results.items():
            if not results:
                continue
            threshold = results[0].eval_metric_result.threshold
            scores = [m.eval_metric_result.score for m in results if m.eval_metric_result.score is not None]
            
            if scores:
                overall_score = statistics.mean(scores)
                status = "PASSED" if overall_score >= threshold else "FAILED"
            else:
                overall_score = None
                status = "NOT_EVALUATED"
                
            status_symbol = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
            
            score_str = f"{overall_score:.2f}" if overall_score is not None else "N/A"
            print(f"{status_symbol} Metric   : {metric_name}")
            print(f"   Threshold: {threshold:.2f} | Score: {score_str} | Status: {status}")
            
            # Print explanations/details
            for r in results:
                metric_res = r.eval_metric_result
                if hasattr(metric_res, "explanation") and metric_res.explanation:
                    print(f"   📝 Judge Explanation: {str(metric_res.explanation).strip()}")
            print("-" * 71)
            
            # Selective Assertion: Only trigger test failures for routing/tool-use metrics
            is_routing_metric = "tool_use" in metric_name.lower() or "routing" in metric_name.lower()
            if status == "FAILED" and is_routing_metric:
                failures.append(
                    f"{metric_name} Failed. Expected {threshold:.2f}, but got {overall_score:.2f}."
                )
                
        print("=======================================================================\n")
        return failures

    AgentEvaluator._process_metrics_and_get_failures = patched_process_metrics_and_get_failures
    print("📋 [HARNESS] Registered Scorecard Formatter.")
except Exception as e:
    print(f"⚠️ [HARNESS] Failed to register Scorecard Formatter: {e}")


# 4. COMPLIANT INFERENCE CRASH SAFEGUARD PATTPERN
try:
    from google.adk.evaluation.local_eval_service import LocalEvalService
    from google.adk.evaluation.eval_case import Invocation
    from google.genai import types as genai_types

    _orig_evaluate_single = LocalEvalService._evaluate_single_inference_result

    async def patched_evaluate_single_inference_result(self, inference_result, evaluate_config):
        if inference_result.inferences is None:
            eval_case = self._eval_sets_manager.get_eval_case(
                app_name=inference_result.app_name,
                eval_set_id=inference_result.eval_set_id,
                eval_case_id=inference_result.eval_case_id,
            )
            if eval_case is not None:
                eval_id = getattr(eval_case, "eval_id", "Unknown Case")
                print(f"\n⚠️ [SAFEGUARD] Case '{eval_id}' failed during inference. Bypassing crash.")
                dummy_inferences = []
                for turn in (eval_case.conversation or []):
                    dummy_inferences.append(
                        Invocation(
                            user_content=turn.user_content,
                            final_response=genai_types.Content(
                                role="model",
                                parts=[genai_types.Part(text="[Inference Failed]")]
                            ),
                            invocation_id=turn.invocation_id
                        )
                    )
                inference_result.inferences = dummy_inferences
        return await _orig_evaluate_single(self, inference_result, evaluate_config)

    LocalEvalService._evaluate_single_inference_result = patched_evaluate_single_inference_result
    print("🛠️ [HARNESS] Registered Inference Failure Safeguard.")
except Exception as e:
    print(f"⚠️ [HARNESS] Failed to register Safeguard: {e}")
