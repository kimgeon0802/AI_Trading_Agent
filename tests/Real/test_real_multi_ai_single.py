import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Set up path to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env explicitly from root
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

def run_test():
    print("[STEP 5] Starting Real Multi-AI E2E Integration Test")
    
    # 1. Pipeline execution to get candidate
    pipeline = MarketPipeline()
    validated_candidates = pipeline.run()
    
    if validated_candidates.empty:
        print("[FAIL] No candidates found.")
        return

    # Select top 1 candidate
    candidate_df = validated_candidates.iloc[[0]]
    ticker = candidate_df.iloc[0]['ticker']
    
    # 2. Prepare Data (including real Macro)
    # DB initialization
    db_path = "data/test_trading.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DatabaseManager(db_path=db_path)
    
    # Macro Manager
    macro_manager = MacroManager(db)
    macro_data = macro_manager.fetch_and_save_macro_data()
    
    # Adapter
    adapter = MarketDataAdapter()
    adapter_data_list = adapter.convert_candidates(candidate_df, {}, macro_data)
    adapter_data = adapter_data_list[0]
    
    # 3. Create Prediction entry for foreign key
    cursor = db.connection.cursor()
    cursor.execute(
        "INSERT INTO predictions (timestamp, ticker, prediction) VALUES (?, ?, ?)",
        (adapter_data["timestamp"], ticker, "PENDING")
    )
    prediction_id = cursor.lastrowid
    db.connection.commit()
    print(f"[INFO] Created prediction_id: {prediction_id}")
    
    # 4. MultiAIOrchestrator Execution
    orchestrator = MultiAIOrchestrator(db)
    
    print(f"[INFO] Running E2E for candidate: {ticker}...")
    
    # Log Configs
    print(f"[INFO] Config: USE_MOCK_AI={os.getenv('USE_MOCK_AI')}, "
          f"USE_MOCK_CLAUDE={os.getenv('USE_MOCK_CLAUDE')}, "
          f"CLAUDE_MODEL={os.getenv('CLAUDE_MODEL')}")
    
    try:
        final_result = orchestrator.execute(adapter_data, prediction_id=prediction_id)
        
        if final_result:
            print("[SUCCESS] E2E Integration successful.")
            print(f"[INFO] Final Decision: {json.dumps(final_result, indent=2, ensure_ascii=False)}")
        else:
            print("[FAIL] Orchestrator returned None.")
            
    except Exception as e:
        print(f"[ERROR] Exception during E2E call: {e}")

if __name__ == "__main__":
    run_test()
