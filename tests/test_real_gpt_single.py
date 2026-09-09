import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Set up path to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Force real AI mode for this test
os.environ["USE_MOCK_AI"] = "false"
load_dotenv(override=True)

from market.pipeline import MarketPipeline
from market.screening_engine import ScreeningEngine
from market.candidate_validator import CandidateValidator
from market.market_data_adapter import MarketDataAdapter
from agents.gpt_agent.agent import GPTAgent

def run_test():
    print("[STEP 2] Starting Real GPT Single-Stock Test")
    
    # 1. Pipeline execution to get candidate
    pipeline = MarketPipeline()
    validated_candidates = pipeline.run()
    
    if validated_candidates.empty:
        print("[FAIL] No candidates found.")
        return

    # Select top 1 candidate
    candidate_row = validated_candidates.iloc[0]
    ticker = candidate_row['ticker']
    name = candidate_row['name']
    market = candidate_row['market']
    
    print(f"[INFO] Selected Candidate: {ticker} ({name}) - {market}")
    
    # 2. MarketDataAdapter
    adapter = MarketDataAdapter()
    # Prepare data for a single candidate
    # convert_candidates expects a DataFrame
    candidate_df = validated_candidates.iloc[[0]]
    adapter_data_list = adapter.convert_candidates(candidate_df, {}, {})
    adapter_data = adapter_data_list[0]
    
    # 3. GPTAgent Execution
    gpt_agent = GPTAgent()
    
    print("[INFO] Calling OpenAI API...")
    try:
        decision = gpt_agent.make_decision(adapter_data)
        
        if decision:
            print("[SUCCESS] Decision object created successfully.")
            print(f"[INFO] Decision: {json.dumps(decision, indent=2, ensure_ascii=False)}")
        else:
            print("[FAIL] GPTAgent returned None.")
            
    except Exception as e:
        print(f"[ERROR] Exception during GPTAgent call: {e}")

if __name__ == "__main__":
    run_test()
