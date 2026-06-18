# topology_isolated_template.py
# Reference implementation for Option 1: Isolated Per-Turn Evaluation
# This is the native ADK approach where each conversation turn is evaluated in a silo.

import asyncio
from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_case import EvalCase

class IsolatedTurnEvaluator:
    """
    Demonstrates how to run isolated per-turn evaluations.
    This is best for strict compliance testing where context is irrelevant.
    """
    
    @staticmethod
    async def evaluate_turn(user_input: str, agent_response: str, rubric: str) -> dict:
        """
        Evaluates a single turn in complete isolation.
        Pros: High precision on literal output.
        Cons: High API cost, blind to previous turns.
        """
        print(f"🔍 [ISOLATED] Grading single turn: '{user_input[:20]}...'")
        
        # Native ADK evaluations handle this under the hood during AgentEvaluator.evaluate()
        # This function illustrates the conceptual API call the ADK makes.
        
        prompt = f"""
        Evaluate the agent's response to the user's input based on the following rubric.
        
        Rubric: {rubric}
        User Input: {user_input}
        Agent Response: {agent_response}
        
        Did the agent fulfill the rubric? Respond only with 1.0 for Yes, or 0.0 for No.
        """
        
        # In a real run, this is handled by google.adk.models.google_llm
        return {
            "score": 1.0,
            "rationale": "Evaluated in isolation successfully."
        }

    @staticmethod
    async def run_suite(dataset_path: str):
        """Executes the standard isolated ADK evaluation runner."""
        print("🚀 Starting Isolated Per-Turn Evaluation (Native ADK)")
        
        # This natively triggers the isolated per-turn metric judges defined in test_config.json
        await AgentEvaluator.evaluate(
            agent_module="src.agents",
            eval_dataset_file_path_or_dir=dataset_path
        )
