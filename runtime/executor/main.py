import asyncio
import logging
import os
from datetime import datetime

from market.pipeline import MarketPipeline
from agents.multi_ai.orchestrator import MultiAIOrchestrator

from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.portfolio_manager import PortfolioManager
from runtime.tool_manager.evaluation_manager import EvaluationManager
from runtime.tool_manager.market_simulator import MarketSimulator
from runtime.tool_manager.sentiment_analyzer import SentimentAnalyzer
from runtime.tool_manager.macro_manager import MacroManager
from runtime.tool_manager.risk_manager import RiskManager


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/runtime.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("RuntimeExecutor")


# ============================================================
# Runtime Executor
# ============================================================

class RuntimeExecutor:

    def __init__(self, db_path="data/trading.db"):

        # ----------------------------------------------------
        # Core Runtime Components
        # ----------------------------------------------------

        self.db = DatabaseManager(
            db_path=db_path
        )

        self.portfolio_manager = PortfolioManager(
            self.db
        )

        self.evaluation_manager = EvaluationManager(
            self.db
        )

        self.market_simulator = MarketSimulator()

        self.sentiment_analyzer = SentimentAnalyzer()

        self.macro_manager = MacroManager(
            self.db
        )

        self.risk_manager = RiskManager(
            self.db
        )
        
        self.market_pipeline = MarketPipeline()

        # ----------------------------------------------------
        # Multi-AI Orchestrator
        #
        # GPT / Claude / Mock / Real / Consensus
        # are handled inside the orchestrator.
        # ----------------------------------------------------

        logger.info(
            "Initializing MultiAIOrchestrator"
        )

        self.agent = MultiAIOrchestrator(
            self.db
        )

        # ----------------------------------------------------
        # Initialize Virtual Portfolio
        # ----------------------------------------------------

        self.portfolio_manager.ensure_initial_portfolio()

        # ----------------------------------------------------
        # Display Current AI Configuration
        # ----------------------------------------------------

        self.use_mock_ai = os.environ.get(
            "USE_MOCK_AI",
            "true"
        ).strip().lower() == "true"

        self.use_mock_claude = os.environ.get(
            "USE_MOCK_CLAUDE",
            "true"
        ).strip().lower() == "true"
        
        self.is_real_ai_mode = (
            not self.use_mock_ai
            and not self.use_mock_claude
        )

        logger.info(
            f"AI Configuration - "
            f"USE_MOCK_AI={self.use_mock_ai}, "
            f"USE_MOCK_CLAUDE={self.use_mock_claude}, "
            f"IS_REAL_AI_MODE={self.is_real_ai_mode}"
        )


    # ========================================================
    # Trading Cycle
    # ========================================================

    async def run_cycle(self, market_condition=None):

        logger.info(
            "Starting new trading cycle..."
        )

        # ----------------------------------------------------
        # Run based on Mode
        # ----------------------------------------------------
        
        if self.is_real_ai_mode:
            await self._run_real_ai_cycle(market_condition)
        else:
            await self._run_mock_cycle(market_condition)

    async def _run_mock_cycle(self, market_condition=None):
        """
        기존 MOCK 테스트 파이프라인
        """

        # ----------------------------------------------------
        # 0. Simulate Market Movement
        # ----------------------------------------------------

        if market_condition:
            self.market_simulator.set_condition(
                market_condition
            )

        self.market_simulator.simulate_step()

        # ----------------------------------------------------
        # Target Ticker
        # ----------------------------------------------------

        target_ticker = "005930"

        current_price = self.market_simulator.get_price(
            target_ticker
        )

        # ----------------------------------------------------
        # 1. Collect Market Data
        # ----------------------------------------------------

        market_data = self._collect_data(
            target_ticker,
            current_price
        )

        logger.info(
            f"Requesting decision from AI agent "
            f"for {target_ticker} "
            f"at price {current_price}..."
        )

        # ----------------------------------------------------
        # 2. Create Prediction Record
        #
        # One prediction_id is used as the traceability key
        # for GPT / Claude / Consensus / Trade / Evaluation.
        # ----------------------------------------------------

        timestamp = datetime.now().isoformat()

        prediction_id = self.db.save_prediction(
            target_ticker,
            "PENDING",
            0.0,
            0.0,
            "Multi-AI Pending",
            timestamp
        )

        logger.info(
            f"Created prediction record: "
            f"prediction_id={prediction_id}"
        )

        # ----------------------------------------------------
        # 3. Execute Multi-AI Pipeline
        # ----------------------------------------------------

        decision_result = None

        try:

            decision_result = self.agent.execute(
                market_data,
                prediction_id
            )

        except Exception as e:

            logger.exception(
                f"Multi-AI execution failed: {e}"
            )

            decision_result = None

        # ----------------------------------------------------
        # 4. Validate / Save Final Decision
        # ----------------------------------------------------

        if decision_result:

            decision = decision_result.get(
                "decision",
                "HOLD"
            )

            confidence = decision_result.get(
                "confidence",
                0.0
            )

            reasoning = decision_result.get(
                "reasoning",
                "No reasoning provided"
            )

            risks = decision_result.get(
                "risks",
                []
            )

            self.db.execute_query(
                """
                UPDATE predictions
                SET prediction = ?,
                    confidence = ?,
                    reasoning = ?
                WHERE id = ?
                """,
                (
                    decision,
                    confidence,
                    str(reasoning),
                    prediction_id
                )
            )

            logger.info(
                f"AI Decision for {target_ticker}: "
                f"{decision} "
                f"(Confidence: {confidence})"
            )

            # ------------------------------------------------
            # 5. Save Reasoning
            # ------------------------------------------------

            self.db.save_reasoning(
                decision,
                reasoning,
                risks,
                confidence,
                datetime.now().isoformat(),
                prediction_id=prediction_id
            )

            # ------------------------------------------------
            # 6. Execute Virtual Portfolio Decision
            # ------------------------------------------------

            self.portfolio_manager.execute_decision(
                target_ticker,
                decision_result,
                current_price,
                prediction_id=prediction_id
            )

        else:

            logger.error(
                "Failed to get valid decision from AI. "
                "Falling back to HOLD."
            )

            decision_result = {
                "decision": "HOLD",
                "confidence": 0.0,
                "reasoning": (
                    "Failed to get valid decision "
                    "from AI"
                ),
                "risks": [
                    "AI decision unavailable"
                ]
            }

            self.db.execute_query(
                """
                UPDATE predictions
                SET prediction = ?,
                    confidence = ?,
                    reasoning = ?
                WHERE id = ?
                """,
                (
                    "HOLD",
                    0.0,
                    "Failed to get valid decision from AI",
                    prediction_id
                )
            )

            self.db.save_reasoning(
                "HOLD",
                decision_result["reasoning"],
                decision_result["risks"],
                0.0,
                datetime.now().isoformat(),
                prediction_id=prediction_id
            )

            self.portfolio_manager.execute_decision(
                target_ticker,
                decision_result,
                current_price,
                prediction_id=prediction_id
            )

        # ----------------------------------------------------
        # 7. Run Evaluation
        # ----------------------------------------------------

        evaluation_market_data = (
            self.market_simulator.get_all_prices()
        )

        self.evaluation_manager.run_evaluation(
            evaluation_market_data
        )

        logger.info(
            f"Trading cycle completed "
            f"for prediction_id={prediction_id}"
        )

    async def _run_real_ai_cycle(self, market_condition=None):
        """
        MarketPipeline 기반 실제 AI 분석 파이프라인
        """
        
        logger.info("Running REAL AI mode pipeline...")
        
        # 1. MarketPipeline 실행
        candidates = self.market_pipeline.run()
        
        if candidates.empty:
            logger.info("[INFO] No validated candidates found. Skipping AI analysis.")
            return

        # 2. Top N 후보 선정
        max_candidates = int(os.environ.get("MAX_GPT_CANDIDATES", 5))
        top_candidates = candidates.head(max_candidates)
        
        logger.info(f"[INFO] Analyzing Top {len(top_candidates)} candidates.")
        
        # 3. 각 후보별 분석 (예시 흐름 - 추후 상세 구현 필요)
        for _, candidate in top_candidates.iterrows():
            ticker = candidate["ticker"]
            price = candidate["close"]
            
            logger.info(f"[INFO] Analyzing candidate: {ticker} ({candidate['name']})")
            
            # 여기서부터 GPT/Claude 분석 로직 연결 (구조는 _run_mock_cycle 참고)
            # prediction 기록 생성, agent.execute() 호출, Portfolio 연결 등
            
            # --- (이후 작업에서 이 부분을 구체화합니다) ---


    # ========================================================
    # Market / Context Data Collection
    # ========================================================

    def _collect_data(self, ticker, price):

        # ----------------------------------------------------
        # Portfolio State
        # ----------------------------------------------------

        portfolio_state = (
            self.portfolio_manager.get_current_state()
        )

        # ----------------------------------------------------
        # Macro Data
        # ----------------------------------------------------

        self.macro_manager.fetch_and_save_macro_data()

        macro_data = (
            self.macro_manager.get_current_macro_indicators()
        )

        # ----------------------------------------------------
        # Simulated News
        # ----------------------------------------------------

        news_data = [

            {
                "title": "삼성전자 1분기 영업이익 예상 상회",
                "source": "경제뉴스",
                "summary": (
                    "반도체 부문 흑자 전환 성공으로 "
                    "시장 기대치 상회하는 실적 발표."
                ),
                "published_at": datetime.now().strftime(
                    "%Y-%m-%d"
                )
            },

            {
                "title": (
                    "글로벌 경기 둔화 우려에 "
                    "반도체 수요 불확실성 증대"
                ),
                "source": "국제금융",
                "summary": (
                    "금리 인상 장기화로 인한 소비 위축이 "
                    "테크 기업 실적에 영향 줄 가능성."
                ),
                "published_at": datetime.now().strftime(
                    "%Y-%m-%d"
                )
            }

        ]

        # ----------------------------------------------------
        # Sentiment Analysis
        # ----------------------------------------------------

        sentiment_result = (
            self.sentiment_analyzer.analyze_news_list(
                news_data
            )
        )

        # ----------------------------------------------------
        # Risk Assessment
        # ----------------------------------------------------

        risk_report = (
            self.risk_manager.get_risk_report(
                ticker,
                price,
                macro_data=macro_data
            )
        )

        # ----------------------------------------------------
        # Final Market Data
        # ----------------------------------------------------

        return {

            "timestamp": datetime.now().isoformat(),

            "market_summary": {

                "kospi": 2750.45,

                "nasdaq": 16345.22,

                "condition": (
                    self.market_simulator.current_condition
                )

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


# ============================================================
# Standalone Execution
# ============================================================

async def main():

    executor = RuntimeExecutor()

    await executor.run_cycle()


if __name__ == "__main__":

    asyncio.run(main())