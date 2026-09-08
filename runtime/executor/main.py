import asyncio
import logging
import os
from datetime import datetime

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

        use_mock_ai = os.environ.get(
            "USE_MOCK_AI",
            "true"
        ).strip().lower()

        use_mock_claude = os.environ.get(
            "USE_MOCK_CLAUDE",
            "true"
        ).strip().lower()

        logger.info(
            f"AI Configuration - "
            f"USE_MOCK_AI={use_mock_ai}, "
            f"USE_MOCK_CLAUDE={use_mock_claude}"
        )


    # ========================================================
    # Trading Cycle
    # ========================================================

    async def run_cycle(self, market_condition=None):

        logger.info(
            "Starting new trading cycle..."
        )

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
        #
        # MultiAIOrchestrator handles:
        # - Mock GPT
        # - Real GPT
        # - Mock Claude
        # - Real Claude
        # - Retry
        # - Credit Exhausted
        # - Consensus
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

            # ------------------------------------------------
            # Update the existing prediction.
            #
            # Do NOT create another prediction row.
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Logging
            # ------------------------------------------------

            logger.info(
                f"AI Decision for {target_ticker}: "
                f"{decision} "
                f"(Confidence: {confidence})"
            )

            # ------------------------------------------------
            # Multi-AI Trace Logging
            # ------------------------------------------------

            consensus = decision_result.get(
                "consensus"
            )

            if consensus:

                logger.info(
                    f"Consensus Decision: {decision}"
                )

                logger.info(
                    f"Consensus Method: "
                    f"{consensus.get('method', 'unknown')}"
                )

            agent_results = decision_result.get(
                "agent_results",
                {}
            )

            for agent_name, result in agent_results.items():

                if not result:

                    logger.info(
                        f" -> {agent_name.upper()}: "
                        f"Failed/None"
                    )

                    continue

                if agent_name.lower() == "gpt":

                    logger.info(
                        f" -> GPT: "
                        f"{result.get('decision', 'UNKNOWN')} "
                        f"(Confidence: "
                        f"{result.get('confidence', 0.0)})"
                    )

                elif agent_name.lower() == "claude":

                    logger.info(
                        f" -> CLAUDE: "
                        f"{result.get('evaluation', 'UNKNOWN')} "
                        f"(Score: "
                        f"{result.get('score', 0.0)})"
                    )

                else:

                    logger.info(
                        f" -> {agent_name.upper()}: "
                        f"{result}"
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

            # ------------------------------------------------
            # AI failure -> HOLD
            #
            # Keep prediction record.
            # Never leave PENDING behind.
            # ------------------------------------------------

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

            # ------------------------------------------------
            # HOLD is passed to PortfolioManager.
            # It should perform no transaction.
            # ------------------------------------------------

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