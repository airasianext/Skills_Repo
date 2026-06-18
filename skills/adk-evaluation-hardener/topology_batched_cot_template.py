# topology_batched_cot_template.py
# Reference implementation for Option 2: Consolidated Trajectory Evaluation
# Demonstrates batching an entire multi-turn dialogue into a single LLM Judge API request,
# using Structured Outputs and Turn-by-Turn Chain-of-Thought to prevent attention dilution.

import asyncio
import json
from google.genai import types
from google.genai import Client

# 1. Define the Structured Pydantic Output Model for the Batch Judge
# On Python 3.13, you can use native type hints or Pydantic models for structured outputs
try:
    from pydantic import BaseModel, Field

    class TurnEvaluation(BaseModel):
        turn_number: int = Field(description="The sequential turn number starting from 1.")
        user_message: str = Field(description="The user's query for this turn.")
        agent_response: str = Field(description="The agent's response for this turn.")
        clinical_rationale: str = Field(description="Mandatory step-by-step reasoning explaining if the rubric was satisfied.")
        routing_score: float = Field(description="Score between 0.0 (Failed) and 1.0 (Passed) for this turn.")

    class BatchEvaluationResult(BaseModel):
        conversation_id: str
        overall_rationale: str
        turn_evaluations: list[TurnEvaluation]
except ImportError:
    # Fallback to standard schema dictionary if pydantic is not present
    BatchEvaluationResult = None

class ConsolidatedBatchEvaluator:
    """
    Consolidates an entire multi-turn dialogue into a single LLM request.
    Pros: 85%+ API call savings, fully context-aware, extremely fast.
    Cons: Requires structured output schemas to prevent attention dilution.
    """
    
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.client = Client()
        self.model_name = model_name

    async def evaluate_conversation_batch(self, conversation_id: str, turns: list[dict], rubric: str) -> dict:
        """
        Sends the entire conversation to Gemini in a single batched call.
        """
        print(f"📊 [BATCH] Grading entire conversation {conversation_id} containing {len(turns)} turns in a single call...")
        
        # 1. Format the conversation transcript cleanly
        transcript_lines = []
        for idx, turn in enumerate(turns):
            transcript_lines.append(f"Turn {idx+1}:")
            transcript_lines.append(f"  User: {turn.get('user_message')}")
            transcript_lines.append(f"  Agent: {turn.get('agent_response')}")
        transcript = "\n".join(transcript_lines)

        # 2. Build the system instruction and prompt
        prompt = f"""
        You are an expert QA Judge. Your task is to evaluate the following multi-turn conversation trace turn-by-turn against the provided rubric.
        
        Rubric Requirements:
        {rubric}
        
        Conversation Transcript:
        {transcript}
        
        Instructions:
        For every turn, you MUST write out your 'clinical_rationale' FIRST, explaining your turn analysis before outputting the 'routing_score' (1.0 or 0.0).
        """

        # 3. Call Gemini with Structured JSON Schema enforcement
        # This guarantees the model outputs a parseable, turn-by-turn array.
        try:
            if BatchEvaluationResult:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=BatchEvaluationResult,
                        temperature=0.0 # Force determinism
                    )
                )
                return json.loads(response.text)
            else:
                # Standard raw JSON fallback
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ [BATCH] Failed to evaluate batch: {e}")
            return {}

# Example Usage Demonstration
if __name__ == "__main__":
    evaluator = ConsolidatedBatchEvaluator()
    
    # Mocking a long, multi-turn conversation trace
    sample_turns = [
        {"user_message": "Hi, I need to correct my name on booking EBCS2B.", "agent_response": "I can help. Please provide your booking number."},
        {"user_message": "My booking number is EBCS2B.", "agent_response": "Thanks. Before I proceed, do you have your valid passport ready?"},
        {"user_message": "Yes I do.", "agent_response": "Perfect! Calling the name correction specialist to update John Dor to John Doe."}
    ]
    
    sample_rubric = "The agent must ask for the PNR booking number and remind the user to have a valid document (passport) ready before proceeding."
    
    # Run the batch evaluation
    result = asyncio.run(evaluator.evaluate_conversation_batch(
        conversation_id="name-correction-001",
        turns=sample_turns,
        rubric=sample_rubric
    ))
    
    print("\n📦 [BATCH EVALUATION SCORECARD] Final Structured JSON Result:")
    print(json.dumps(result, indent=2))
