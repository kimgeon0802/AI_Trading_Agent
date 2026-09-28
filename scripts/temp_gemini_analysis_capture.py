import os
import json
from agents.gemini_agent.agent import GeminiAgent
from market.market_data_collector import MarketDataCollector
from market.screening_engine import ScreeningEngine
from market.market_data_adapter import MarketDataAdapter
from runtime.tool_manager.refinement_engine import RefinementEngine
from dotenv import load_dotenv

load_dotenv()

# Setup
collector = MarketDataCollector()
screening = ScreeningEngine()
refinement = RefinementEngine(target_min=10, target_max=15)
adapter = MarketDataAdapter()
gemini_agent = GeminiAgent()

# Pipeline
market_df = collector.collect_all_markets()
candidates = screening.run(market_df)
refined = refinement.refine(candidates)
historical_data_map = {row['ticker']: collector.get_historical_ohlcv(row['ticker'], days=100) for _, row in refined.iterrows()}
gemini_dataset = adapter.convert_candidates(refined, historical_data_map=historical_data_map)

# Gemini API call
os.environ["USE_MOCK_AI"] = "false"
result = gemini_agent.execute_batch(gemini_dataset)
print(json.dumps(result, indent=2))
