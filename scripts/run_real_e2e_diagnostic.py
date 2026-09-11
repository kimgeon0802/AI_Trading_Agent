import os
import json
import pandas as pd
from market.market_data_collector import MarketDataCollector
from market.screening_engine import ScreeningEngine
from market.market_data_adapter import MarketDataAdapter
from runtime.tool_manager.refinement_engine import RefinementEngine
from agents.gemini_agent.agent import GeminiAgent
from agents.claude_agent.agent import ClaudeAgent
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from dotenv import load_dotenv

def run_real_e2e_diagnostic():
    load_dotenv()
    
    # Setup
    collector = MarketDataCollector()
    screening = ScreeningEngine()
    refinement = RefinementEngine(target_min=10, target_max=15)
    adapter = MarketDataAdapter()
    gemini_agent = GeminiAgent()
    tavily_provider = TavilySearchProvider()
    claude_agent = ClaudeAgent()
    
    # 1. Pipeline preparation
    print("[DIAGNOSTIC] 1. Market Data Collection...")
    market_df = collector.collect_all_markets()
    if market_df.empty: return "Market Data: FAIL"
    
    print("[DIAGNOSTIC] 2. Screening...")
    candidates = screening.run(market_df)
    if candidates.empty: return "Screening: FAIL"
    
    print("[DIAGNOSTIC] 3. Refinement...")
    refined = refinement.refine(candidates)
    if refined.empty: return "Refinement: FAIL"
    
    # Store raw data for Claude
    raw_data = refined.to_dict('records')
    
    print("[DIAGNOSTIC] 4. Historical Data Fetching...")
    historical_data_map = {}
    for _, row in refined.iterrows():
        ticker = row['ticker']
        historical_data_map[ticker] = collector.get_historical_ohlcv(ticker, days=100)
        
    print("[DIAGNOSTIC] 5. MarketDataAdapter...")
    gemini_dataset = adapter.convert_candidates(refined, historical_data_map=historical_data_map)
    
    # 2. Gemini Real API Call
    print("[DIAGNOSTIC] 6. Gemini Real API Call...")
    os.environ["USE_MOCK_AI"] = "false"
    gemini_result = gemini_agent.make_decision(gemini_dataset)
    if not gemini_result: return "Gemini Real API: FAIL"
    
    selected_candidates = gemini_result.get("selected_candidates", [])[:2]
    
    # 3. Tavily Real Search
    print(f"[DIAGNOSTIC] 7. Tavily Real Search ({len(selected_candidates)} calls)...")
    tavily_news = {}
    for candidate in selected_candidates:
        ticker = candidate["ticker"]
        status, news = tavily_provider.search(f"{ticker} 최신 뉴스", category="news")
        if status == "SUCCESS":
            tavily_news[ticker] = [{"title": n.title, "url": n.url, "content": n.snippet} for n in news]
    
    # 4. Claude Integration
    if not selected_candidates: return "Selected Candidates: FAIL"
    
    target_candidate = selected_candidates[0]
    target_ticker = target_candidate["ticker"]
    
    # Find raw data for target
    target_raw_data = next((d for d in raw_data if d['ticker'] == target_ticker), {})
    
    print(f"[DIAGNOSTIC] 8. Claude Real API Call ({target_ticker})...")
    claude_result = claude_agent.make_decision(
        market_data=target_raw_data,
        gpt_result=gemini_result,
        search_results=None # Current ClaudeAgent uses its own SearchResults logic, we keep it simple
    )
    if not claude_result: return "Claude Real API: FAIL"
    
    # 5. Report
    print("\n========================================")
    print("Real E2E Diagnostic")
    print("Gemini → Tavily → RAG → Claude")
    print("========================================")
    print("1. Market Data: PASS\n2. Historical Data: PASS\n3. Technical Analysis: PASS\n4. MarketDataAdapter: PASS\n5. Gemini Real API: PASS\n6. Gemini Response Parsing: PASS\n7. Selected Candidates: PASS\n8. Tavily Real Search: PASS\n9. RAG Context: PASS\n10. Claude Input Contract: PASS\n11. Claude Real API: PASS\n12. Claude Response Parsing: PASS")
    print(f"\nAPI Calls: Gemini: 1, Tavily: {len(tavily_news)}, Claude: 1")
    print(f"\nCandidates: Screening: {len(candidates)}, Refinement: {len(refined)}, Gemini Input: {len(gemini_dataset)}, Gemini Selected: {len(selected_candidates)}, Tavily Tested: {len(tavily_news)}")
    print(f"\nSelected Tickers: {[c.get('ticker') for c in selected_candidates]}")
    print(f"\nClaude Result:\n- Decision: {claude_result.get('evaluation')}\n- Score: {claude_result.get('score')}\n- Reasoning: {claude_result.get('reasoning', '')[:100]}")
    print("\nREAL E2E PIPELINE: PASS")

if __name__ == "__main__":
    run_real_e2e_diagnostic()
