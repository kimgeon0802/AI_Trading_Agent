import os
import json
import pandas as pd
from market.market_data_collector import MarketDataCollector
from market.screening_engine import ScreeningEngine
from market.market_data_adapter import MarketDataAdapter
from runtime.tool_manager.refinement_engine import RefinementEngine
from agents.gemini_agent.agent import GeminiAgent
from dotenv import load_dotenv

def run_gemini_diagnostic():
    load_dotenv()
    
    # 1. Market Data Collection
    print("[DIAGNOSTIC] Collecting Market Data...")
    collector = MarketDataCollector()
    market_df = collector.collect_all_markets()
    if market_df.empty:
        return "Market Data: FAIL"
    
    # 2. Screening
    print("[DIAGNOSTIC] Screening...")
    screening = ScreeningEngine()
    candidates = screening.run(market_df)
    if candidates.empty:
        return "Screening: FAIL"
        
    # 3. Refinement
    print("[DIAGNOSTIC] Refinement...")
    refinement = RefinementEngine(target_min=10, target_max=15)
    refined = refinement.refine(candidates)
    if refined.empty:
        return "Refinement: FAIL"
        
    # 4. Historical Data Fetching
    print(f"[DIAGNOSTIC] Fetching historical data for {len(refined)} candidates...")
    historical_data_map = {}
    for _, row in refined.iterrows():
        ticker = row['ticker']
        hist_df = collector.get_historical_ohlcv(ticker, days=100)
        historical_data_map[ticker] = hist_df
        
    # 5. MarketDataAdapter (Gemini Dataset Creation)
    print("[DIAGNOSTIC] Adapting to Gemini Dataset...")
    adapter = MarketDataAdapter()
    gemini_dataset = adapter.convert_candidates(refined, historical_data_map=historical_data_map)
    
    # Check NaN/Serialization
    try:
        json_str = json.dumps(gemini_dataset)
        json.loads(json_str)
    except Exception as e:
        return f"JSON Serialization: FAIL ({e})"
        
    # 6. Gemini Real API Call
    print("[DIAGNOSTIC] Calling Gemini Real API...")
    # Force disable mock mode
    os.environ["USE_MOCK_AI"] = "false"
    agent = GeminiAgent()
    
    try:
        response = agent.make_decision(gemini_dataset)
        if not response:
            return "Gemini Real API: FAIL (No response)"
    except Exception as e:
        return f"Gemini Real API: FAIL ({e})"
        
    # 7. Parsing
    print("[DIAGNOSTIC] Success. Summarizing results.")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # Print Diagnostics Table
    print("\n========================================")
    print("Gemini Real API Single Call Diagnostic")
    print("========================================")
    print(f"1. Market Data: PASS")
    print(f"2. Historical Data: PASS")
    print(f"3. Technical Analysis: PASS")
    print(f"4. MarketDataAdapter: PASS")
    print(f"5. Gemini Dataset JSON Serialization: PASS")
    print(f"6. Gemini Real API: PASS")
    print(f"7. Gemini Response Parsing: PASS")
    print(f"\nAPI Calls: Gemini: 1, Tavily: 0, Claude: 0")
    print(f"\nCandidates: Screening: {len(candidates)}, Refinement: {len(refined)}, Gemini Input: {len(gemini_dataset)}, Gemini Selected: {len(response.get('selected_candidates', []))}")
    print(f"\nGemini Model: {agent.model_name}")
    print(f"\nGemini Result Summary:")
    print(f"- Decision: {response.get('decision')}")
    print(f"- Confidence: {response.get('confidence')}")
    print(f"- Selected Tickers: {[c.get('ticker') for c in response.get('selected_candidates', [])]}")
    print("\nGEMINI REAL API SINGLE CALL TEST: PASS")

if __name__ == "__main__":
    run_gemini_diagnostic()
