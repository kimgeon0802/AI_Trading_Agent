import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Set up path to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env explicitly
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

# Force REAL AI mode
os.environ["USE_MOCK_AI"] = "false"
os.environ["USE_MOCK_CLAUDE"] = "false"

from market.pipeline import MarketPipeline
from market.market_data_adapter import MarketDataAdapter
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.macro_manager import MacroManager
from agents.multi_ai.orchestrator import MultiAIOrchestrator

def run_batch(n_stocks):
    print(f"\n[STEP 6] Starting Real Multi-AI E2E Test for {n_stocks} stocks")
    
    # Setup
    db_path = "data/test_trading.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DatabaseManager(db_path=db_path)
    
    pipeline = MarketPipeline()
    validated_candidates = pipeline.run()
    
    if validated_candidates.empty or len(validated_candidates) < n_stocks:
        print(f"[FAIL] Not enough candidates ({len(validated_candidates)}) for {n_stocks} requested.")
        return

    # Select candidates
    candidates = validated_candidates.iloc[:n_stocks]
    
    # Macro Manager
    macro_manager = MacroManager(db)
    macro_data = macro_manager.fetch_and_save_macro_data()
    
    # Adapter
    adapter = MarketDataAdapter()
    adapter_data_list = adapter.convert_candidates(candidates, {}, macro_data)
    
    # Orchestrator
    orchestrator = MultiAIOrchestrator(db)
    
    results = []
    start_time = time.time()
    
    for i, adapter_data in enumerate(adapter_data_list):
        ticker = adapter_data['ticker']
        print(f"[INFO] Running E2E for candidate {i+1}/{n_stocks}: {ticker}...")
        
        # Create Prediction entry
        cursor = db.connection.cursor()
        cursor.execute(
            "INSERT INTO predictions (timestamp, ticker, prediction) VALUES (?, ?, ?)",
            (adapter_data["timestamp"], ticker, "PENDING")
        )
        prediction_id = cursor.lastrowid
        db.connection.commit()
        
        try:
            final_result = orchestrator.execute(adapter_data, prediction_id=prediction_id)
            results.append({"ticker": ticker, "status": "SUCCESS" if final_result else "FAIL"})
        except Exception as e:
            print(f"[ERROR] Exception for {ticker}: {e}")
            results.append({"ticker": ticker, "status": "FAIL"})
            
    total_time = time.time() - start_time
    print(f"[SUCCESS] Batch finished. Total time: {total_time:.2f}s")
    for r in results:
        print(f"  {r['ticker']}: {r['status']}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=3)
    args = parser.parse_args()
    run_batch(args.n)
