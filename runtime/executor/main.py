import asyncio
import json
import logging
import os
import random
from datetime import datetime
from agents.gpt_agent.agent import GPTAgent
from agents.multi_ai.orchestrator import MultiAIOrchestrator
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.portfolio_manager import PortfolioManager
from runtime.tool_manager.evaluation_manager import EvaluationManager
from runtime.tool_manager.market_simulator import MarketSimulator
from runtime.tool_manager.sentiment_analyzer import SentimentAnalyzer
from runtime.tool_manager.macro_manager import MacroManager
from runtime.tool_manager.risk_manager import RiskManager

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
    def __init__(self, db_path="data/trading.db"):
        self.db = DatabaseManager(db_path=db_path)
        self.portfolio_manager = PortfolioManager(self.db)
        self.evaluation_manager = EvaluationManager(self.db)
        self.market_simulator = MarketSimulator()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.macro_manager = MacroManager(self.db)
        self.risk_manager = RiskManager(self.db)
        
        self.ai_mode = os.environ.get("TRADING_AI_MODE", "single")
        if self.ai_mode == "multi":
            logger.info("Initializing MultiAIOrchestrator")
            self.agent = MultiAIOrchestrator(self.db)
        else:
            logger.info("Initializing GPTAgent")
            self.agent = GPTAgent()
        
        # Initialize portfolio if needed
        self.portfolio_manager.ensure_initial_portfolio()

    async def run_cycle(self, market_condition=None):
        logger.info(f"Starting new trading cycle... (Mode: {self.ai_mode})")
        
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
        
        prediction_id = None
        if self.ai_mode == "multi":
            # 1. Create a dummy prediction record to get ID
            timestamp = datetime.now().isoformat()
            prediction_id = self.db.save_prediction(target_ticker, "PENDING", 0.0, 0.0, "Multi-AI Pending", timestamp)
            
            # 2. Call orchestrator with the prediction_id
            decision_result = self.agent.execute(market_data, prediction_id)
            
            # 3. Update the prediction record with final decision
            if decision_result:
                self.db.execute_query("UPDATE predictions SET prediction = ?, confidence = ?, reasoning = ? WHERE id = ?", 
                                     (decision_result['decision'], decision_result['confidence'], str(decision_result['reasoning']), prediction_id))
            else:
                # Update PENDING prediction to HOLD if failed
                self.db.execute_query("UPDATE predictions SET prediction = 'HOLD', confidence = 0.0, reasoning = 'Failed to get valid decision from AI' WHERE id = ?", (prediction_id,))

        else:
            decision_result = self.agent.make_decision(market_data)
            # Save prediction to get prediction_id
            if decision_result:
                timestamp = datetime.now().isoformat()
                prediction_id = self.db.save_prediction(
                    target_ticker,
                    decision_result['decision'],
                    0.0,
                    decision_result['confidence'],
                    str(decision_result['reasoning']),
                    timestamp
                )
        
        if decision_result:
            timestamp = datetime.now().isoformat()
            
            # Log results based on mode
            if self.ai_mode == "multi":
                logger.info(f"Multi-AI Consensus Decision for {target_ticker}: {decision_result['decision']} (Confidence: {decision_result['confidence']})")
                logger.info(f"Consensus Method: {decision_result['consensus']['method']}")
                for agent, res in decision_result["agent_results"].items():
                    if res:
                        if agent == "gpt":
                            logger.info(f" -> {agent.upper()}: {res['decision']} (Confidence: {res['confidence']})")
                        else: # Claude
                            logger.info(f" -> {agent.upper()}: {res['evaluation']} (Score: {res['score']})")
                    else:
                        logger.info(f" -> {agent.upper()}: Failed/None")
            else:
                logger.info(f"AI Decision for {target_ticker}: {decision_result['decision']} (Confidence: {decision_result['confidence']})")
            
            # 3. Save Reasoning (updated to use prediction_id)
            self.db.save_reasoning(
                decision_result['decision'],
                decision_result['reasoning'],
                decision_result['risks'],
                decision_result['confidence'],
                timestamp,
                prediction_id=prediction_id
            )
            
            # 4. Update Virtual Portfolio (pass prediction_id)
            self.portfolio_manager.execute_decision(target_ticker, decision_result, current_price, prediction_id=prediction_id)
            
            # 5. Run Evaluation for pending predictions
            # In Phase 1 MVP, we evaluate against the current price just generated
            evaluation_market_data = self.market_simulator.get_all_prices()
            self.evaluation_manager.run_evaluation(evaluation_market_data)
            
        else:
            logger.error("Failed to get valid decision from AI.")

    def _collect_data(self, ticker, price):
        portfolio_state = self.portfolio_manager.get_current_state()
        
        # Fetch actual macro data
        self.macro_manager.fetch_and_save_macro_data()
        macro_data = self.macro_manager.get_current_macro_indicators()
        
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
        risk_report = self.risk_manager.get_risk_report(ticker, price, macro_data=macro_data)
        
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
