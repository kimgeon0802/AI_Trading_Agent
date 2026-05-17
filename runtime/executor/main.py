import asyncio
import json
import logging
import os
from datetime import datetime
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.portfolio_manager import PortfolioManager

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
        self.portfolio_manager = PortfolioManager(self.db)
        self.agent = GPTAgent()
        
        # Initialize portfolio if needed
        self.portfolio_manager.ensure_initial_portfolio()

    async def run_cycle(self):
        logger.info("Starting new trading cycle...")
        
        # Target ticker for this cycle
        target_ticker = "005930" # 삼성전자
        current_price = 78500.0  # Mock current price
        
        # 1. Collect Data (Simulated for Phase 1)
        market_data = self._collect_mock_data(target_ticker, current_price)
        
        # 2. Get Decision from AI
        logger.info(f"Requesting decision from AI agent for {target_ticker}...")
        decision_result = self.agent.make_decision(market_data)
        
        if decision_result:
            timestamp = datetime.now().isoformat()
            logger.info(f"AI Decision for {target_ticker}: {decision_result['decision']} (Confidence: {decision_result['confidence']})")
            
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
            
            # 4. Update Virtual Portfolio
            self.portfolio_manager.execute_decision(target_ticker, decision_result, current_price)
            
        else:
            logger.error("Failed to get valid decision from AI.")

    def _collect_mock_data(self, ticker, price):
        portfolio_state = self.portfolio_manager.get_current_state()
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
            "portfolio": portfolio_state,
            "news": [
                {
                    "title": "삼성전자 1분기 영업이익 예상 상회",
                    "source": "경제뉴스",
                    "summary": "반도체 부문 흑자 전환 성공",
                    "published_at": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "technical_indicators": {
                ticker: {
                    "rsi": 55,
                    "macd": 0.5,
                    "price": price
                }
            }
        }

async def main():
    executor = RuntimeExecutor()
    await executor.run_cycle()

if __name__ == "__main__":
    asyncio.run(main())
