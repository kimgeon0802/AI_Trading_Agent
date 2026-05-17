import asyncio
import json
import logging
import os
from datetime import datetime
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/runtime.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RuntimeExecutor")

class RuntimeExecutor:
    def __init__(self):
        self.db = DatabaseManager()
        self.agent = GPTAgent()
        self.portfolio_data = {
            "cash": 10000000,  # 10,000,000 KRW
            "total_asset": 10000000,
            "holdings": []
        }

    async def run_cycle(self):
        logger.info("Starting new trading cycle...")
        
        # 1. Collect Data (Simulated for Phase 1)
        market_data = self._collect_mock_data()
        
        # 2. Get Decision from AI
        logger.info("Requesting decision from AI agent...")
        decision_result = self.agent.make_decision(market_data)
        
        if decision_result:
            timestamp = datetime.now().isoformat()
            logger.info(f"AI Decision: {decision_result['decision']} (Confidence: {decision_result['confidence']})")
            
            # 3. Save Reasoning and Prediction
            self.db.save_reasoning(
                decision_result['decision'],
                decision_result['reasoning'],
                decision_result['risks'],
                decision_result['confidence'],
                timestamp
            )
            
            # Save prediction log as file
            log_filename = f"logs/predictions/prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_filename, "w", encoding="utf-8") as f:
                json.dump(decision_result, f, indent=2, ensure_ascii=False)
            
            # 4. Update Virtual Portfolio (Placeholder for Phase 1)
            self._update_portfolio(decision_result)
            
        else:
            logger.error("Failed to get valid decision from AI.")

    def _collect_mock_data(self):
        # This will be replaced by actual data collectors in later phases
        return {
            "timestamp": datetime.now().isoformat(),
            "market_summary": {
                "kospi": 2750.45,
                "nasdaq": 16345.22,
                "usdkrw": 1350.5
            },
            "macro_data": {
                "interest_rate": 3.5,
                "cpi": 3.1
            },
            "portfolio": self.portfolio_data,
            "news": [
                {
                    "title": "삼성전자 1분기 영업이익 예상 상회",
                    "source": "경제뉴스",
                    "summary": "반도체 부문 흑자 전환 성공",
                    "published_at": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "technical_indicators": {
                "005930": {
                    "rsi": 55,
                    "macd": 0.5
                }
            }
        }

    def _update_portfolio(self, decision):
        # Simple virtual portfolio update logic
        # In Phase 1, we just log that we are "performing" the action
        logger.info(f"Updating virtual portfolio based on decision: {decision['decision']}")
        # Actual logic to update DB and self.portfolio_data would go here

async def main():
    executor = RuntimeExecutor()
    await executor.run_cycle()

if __name__ == "__main__":
    asyncio.run(main())
