import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Set up path to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Force real Claude mode, mock AI (GPT) mode
os.environ["USE_MOCK_CLAUDE"] = "false"
os.environ["USE_MOCK_AI"] = "true" 
load_dotenv(override=True)

from market.pipeline import MarketPipeline
from market.market_data_adapter import MarketDataAdapter
from agents.claude_agent.agent import ClaudeAgent

def run_test():
    print("[STEP 4] Starting Real Claude Single-Stock Test")
    
    # 1. Pipeline execution to get candidate
    pipeline = MarketPipeline()
    validated_candidates = pipeline.run()
    
    if validated_candidates.empty:
        print("[FAIL] No candidates found.")
        return

    # Select top 1 candidate
    candidate_df = validated_candidates.iloc[[0]]
    
    # 2. MarketDataAdapter
    adapter = MarketDataAdapter()
    adapter_data_list = adapter.convert_candidates(candidate_df, {}, {})
    adapter_data = adapter_data_list[0]
    
    # 3. ClaudeAgent Execution
    claude_agent = ClaudeAgent()
    
    # Mock GPT decision
    mock_gpt_result = {
        "decision": "HOLD",
        "confidence": 0.5,
        "reasoning": ["Mock GPT reasoning"],
        "risks": ["Mock GPT risk"],
        "expected_result": "Mock result"
    }
    
    print(f"[INFO] Calling Anthropic API for candidate: {adapter_data['ticker']}...")
    try:
        evaluation = claude_agent.make_decision(adapter_data, mock_gpt_result)
        
        if evaluation:
            print("[SUCCESS] Evaluation object created successfully.")
            print(f"[INFO] Evaluation: {json.dumps(evaluation, indent=2, ensure_ascii=False)}")
        else:
            print("[FAIL] ClaudeAgent returned None.")
            
    except Exception as e:
        print(f"[ERROR] Exception during ClaudeAgent call: {e}")

if __name__ == "__main__":
    run_test()
