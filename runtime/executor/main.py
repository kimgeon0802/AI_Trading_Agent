import asyncio
import json
import logging
import os
from datetime import datetime
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.portfolio_manager import PortfolioManager
from runtime.tool_manager.evaluation_manager import EvaluationManager
from runtime.tool_manager.market_simulator import MarketSimulator
from runtime.tool_manager.sentiment_analyzer import SentimentAnalyzer

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
        self.evaluation_manager = EvaluationManager(self.db)
        self.market_simulator = MarketSimulator()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.agent = GPTAgent()
        
        # Initialize portfolio if needed
        self.portfolio_manager.ensure_initial_portfolio()

    async def run_cycle(self, market_condition=None):
        logger.info("Starting new trading cycle...")
        
        # 0. Simulate Market Movement
        if market_condition:
            self.market_simulator.set_condition(market_condition)
        self.market_simulator.simulate_step()
        
        # Target ticker for this cycle
        target_ticker = "005930" # 삼성전자
        current_price = self.market_simulator.get_price(target_ticker)
        
        # 1. Collect Data (Enhanced for Phase 2)
        market_data = self._collect_data(target_ticker, current_price)
        
        # 2. Get Decision from AI
        logger.info(f"Requesting decision from AI agent for {target_ticker} at price {current_price}...")
        decision_result = self.agent.make_decision(market_data)
        
        if decision_result:
            timestamp = datetime.now().isoformat()
            logger.info(f"AI Decision for {target_ticker}: {decision_result['decision']} (Confidence: {decision_result['confidence']})")
            
            # Save prediction to DB
            self.db.save_prediction(
                target_ticker,
                decision_result['decision'],
                0.0,
                decision_result['confidence'],
                str(decision_result['reasoning']),
                timestamp
            )
            
            # 3. Save Reasoning
            self.db.save_reasoning(
                decision_result['decision'],
                decision_result['reasoning'],
                decision_result['risks'],
                decision_result['confidence'],
                timestamp
            )
            
            # 4. Update Virtual Portfolio
            self.portfolio_manager.execute_decision(target_ticker, decision_result, current_price)
            
            # 5. Run Evaluation for pending predictions
            # In Phase 1 MVP, we evaluate against the current price just generated
            evaluation_market_data = self.market_simulator.get_all_prices()
            self.evaluation_manager.run_evaluation(evaluation_market_data)
            
        else:
            logger.error("Failed to get valid decision from AI.")

    def _collect_data(self, ticker, price):
        portfolio_state = self.portfolio_manager.get_current_state()
        
        # Simulate News
        news_data = [
            {
                "title": "삼성전자 1분기 영업이익 예상 상회",
                "source": "경제뉴스",
                "summary": "반도체 부문 흑자 전환 성공으로 시장 기대치 상회하는 실적 발표.",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "글로벌 경기 둔화 우려에 반도체 수요 불확실성 증대",
                "source": "국제금융",
                "summary": "금리 인상 장기화로 인한 소비 위축이 테크 기업 실적에 영향 줄 가능성.",
                "published_at": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        # Phase 2: Sentiment Analysis
        sentiment_result = self.sentiment_analyzer.analyze_news_list(news_data)
        
        # Phase 2: Risk Assessment
        risk_report = self.risk_manager.get_risk_report(ticker, price)
        
        import random
        # Phase 2: More realistic Macro Data (Simulated)
        macro_data = {
            "interest_rate": 3.5,
            "exchange_rate_usdkrw": round(random.uniform(1320, 1380), 1),
            "cpi": 3.1,
            "fear_greed_index": random.randint(30, 70)
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "market_summary": {
                "kospi": 2750.45,
                "nasdaq": 16345.22,
                "condition": self.market_simulator.current_condition
            },
            "macro_data": macro_data,
            "portfolio": portfolio_state,
            "news": news_data,
            "sentiment_analysis": sentiment_result,
            "risk_report": risk_report,
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
