# user_simulator_template.py
# Reference implementation for using the ADK's native UserSimulator to generate golden dialogue traces.

import asyncio
import json
import os
import sys

# 1. Realignment to resolve local agent dependencies
EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
MONOREPO_ROOT = os.path.dirname(EVAL_DIR)
CONCIERGE_DEV_DIR = os.path.join(MONOREPO_ROOT, "next-concierge-dev")
sys.path.append(CONCIERGE_DEV_DIR)

try:
    from google.adk.evaluation.user_simulator import UserSimulator
    from google.adk.evaluation.eval_case import EvalCase, ConversationScenario
    from google.adk.runners import LocalRunner
    from src.dependencies.config import init as config_init
    print("🛠️ [SIMULATOR] Successfully imported ADK UserSimulator dependencies.")
except ImportError as e:
    print(f"❌ [SIMULATOR] Failed to import ADK dependencies: {e}")
    sys.exit(1)

async def generate_golden_trace_via_simulator(scenario_id, persona, goal, output_path):
    """
    Spins up the ADK UserSimulator to talk to the local agent and saves the Golden dialogue trace.
    """
    # Initialize config to load local Vertex AI / Project configurations
    await config_init()

    # 1. Define the Scenario Persona and Goal
    scenario = ConversationScenario(
        user_persona=persona,
        user_goal=goal
    )
    
    print(f"\n=======================================================================")
    print(f"🚀 Launching ADK UserSimulator for Scenario: {scenario_id}")
    print(f"👤 Persona: {persona}")
    print(f"🎯 Goal: {goal}")
    print(f"=======================================================================\n")

    # 2. Initialize the Simulator (defaults to Gemini for simulating the user)
    # The simulator acts as the user, dynamically generating replies to satisfy the goal.
    simulator = UserSimulator(
        simulator_model="gemini-3-flash-preview", # High-speed conversational model for simulation
        scenario=scenario
    )

    # 3. Initialize your local agent runner
    # Under the hood, this loads your root concierge agent defined in src.agents
    runner = LocalRunner(agent_module="src.agents")

    # 4. Execute the interactive simulation loop
    conversation_turns = []
    max_turns = 10 # Prevent infinite loops if agent/simulator get stuck
    
    # Send the first greeting from the user to kickstart the conversation
    current_user_message = "Hello"
    
    for turn_idx in range(max_turns):
        print(f"🗣️ Turn {turn_idx + 1} | User says: \"{current_user_message}\"")
        
        # Invoke your local agent with the user's message
        agent_response_text = ""
        async for event in runner.run_async(current_user_message):
            if event.content and event.content.parts:
                agent_response_text += "".join([part.text for part in event.content.parts if part.text])
                
        print(f"🤖 Turn {turn_idx + 1} | Agent responds: \"{agent_response_text}\"")
        
        # Record the turn in our Golden Conversation history
        conversation_turns.append({
            "invocation_id": f"turn-{scenario_id}-{turn_idx:03d}",
            "user_content": {
                "role": "user",
                "parts": [{"text": current_user_message}]
            },
            "final_response": {
                "role": "assistant",
                "parts": [{"text": agent_response_text}]
            }
        })

        # Check if the user simulator determines that the goal has been successfully completed
        is_finished, next_reply = await simulator.generate_next_user_reply_async(agent_response_text)
        if is_finished or not next_reply:
            print(f"\n✅ [SIMULATOR] User Simulator reports goal completed successfully!")
            break
            
        current_user_message = next_reply

    # 5. Compile into a standard ADK EvalCase
    eval_case = {
        "eval_id": f"case-simulated-{scenario_id}",
        "session_input": {
            "app_name": "next_concierge",
            "user_id": "test_user_simulated",
            "state": {}
        },
        "conversation": conversation_turns
    }

    # Save to disk
