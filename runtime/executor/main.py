import asyncio
import logging
import os
import json
from datetime import datetime

from market.pipeline import MarketPipeline
from market.market_data_adapter import MarketDataAdapter
from agents.multi_ai.orchestrator import MultiAIOrchestrator
from runtime.tool_manager.refinement_engine import RefinementEngine
from runtime.tool_manager.api_error_handler import APIStatus
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

# Ensure logs directory exists at the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "runtime.log")),
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
        self.refiner = RefinementEngine(target_min=10, target_max=15)
        self.market_data_adapter = MarketDataAdapter()

        # ----------------------------------------------------
        # Multi-AI Orchestrator
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

    def _calculate_overall_status(self, cycle_data: dict) -> str:
        if cycle_data.get("fatal_error"):
            return "FAILED"
            
        candidate_summary = cycle_data.get("candidate_summary", [])
        if not candidate_summary:
            return "FAILED"
            
        statuses = [c["status"] for c in candidate_summary]
        
        if all(s in ("FALLBACK", "FAILED") for s in statuses):
            return "FAILED"
        elif any(s in ("FALLBACK", "FAILED") for s in statuses):
            return "PARTIAL"
        else:
            return "SUCCESS"

    async def run_cycle(self, market_condition=None) -> dict:

        logger.info(
            "Starting new trading cycle..."
        )

        # ----------------------------------------------------
        # Run based on Mode
        # ----------------------------------------------------
        
        if os.environ.get("VALIDATE_ADAPTER_ONLY", "false").lower() == "true":
            await self._run_adapter_validation()
            return {
                "status": "SUCCESS",
                "prediction_ids": [],
                "candidate_summary": [],
                "summary": "Adapter validation completed."
            }
            
        if self.is_real_ai_mode:
            cycle_data = await self._run_real_ai_cycle(market_condition)
        else:
            cycle_data = await self._run_mock_cycle(market_condition)
            
        status = self._calculate_overall_status(cycle_data)
        prediction_ids = cycle_data.get("prediction_ids", [])
        candidate_summary = cycle_data.get("candidate_summary", [])
        
        success_count = sum(1 for c in candidate_summary if c["status"] == "SUCCESS")
        fallback_count = sum(1 for c in candidate_summary if c["status"] in ("FALLBACK", "FAILED"))
        
        summary_msg = (
            f"Trading Cycle completed with Status: {status}. "
            f"Predictions: {len(prediction_ids)}, Succeeded: {success_count}, Fallback/Failed: {fallback_count}"
        )
        
        cycle_result = {
            "status": status,
            "prediction_ids": prediction_ids,
            "candidate_summary": candidate_summary,
            "summary": summary_msg
        }
        logger.info(summary_msg)
        return cycle_result

    async def _run_real_ai_cycle(self, market_condition=None) -> dict:
        """
        Gemini 1차 분석 및 Claude 2차 심층 분석이 포함된 실제 AI 파이프라인.
        """
        logger.info("Starting REAL AI trading cycle...")
        prediction_ids = []
        candidate_summary = []
        
        # 1. Screening & Refinement
        try:
            candidates_df = self.market_pipeline.run()
            refined_df = self.refiner.refine(candidates_df)
        except Exception as e:
            logger.error(f"Market Pipeline / Refinement failed: {e}")
            return {"prediction_ids": [], "candidate_summary": [], "fatal_error": str(e)}
            
        if refined_df.empty:
            logger.warning("No refined candidates found.")
            return {"prediction_ids": [], "candidate_summary": [], "fatal_error": "No candidates found"}
        
        # 2. Historical Data Fetch & Technical Analysis
        from market.market_data_collector import MarketDataCollector
        collector = MarketDataCollector()
        
        # 2.1 Historical Data Optimization: Get all unique tickers first
        unique_tickers = refined_df['ticker'].unique()
        historical_data_map = {}
        for ticker in unique_tickers:
            historical_data_map[ticker] = collector.get_historical_ohlcv(ticker, days=100)
            
        # 3. Market Data Adapter (Gemini Analysis Dataset Creation)
        portfolio_state = self.portfolio_manager.get_current_state()
        self.macro_manager.fetch_and_save_macro_data()
        macro_data = self.macro_manager.get_current_macro_indicators()
        
        gemini_dataset = self.market_data_adapter.convert_candidates(
            refined_df,
            historical_data_map=historical_data_map,
            portfolio_state=portfolio_state,
            macro_data=macro_data
        )
        
        # 4. Gemini Batch 분석
        logger.info(f"Executing Batch AI Pipeline for {len(gemini_dataset)} candidates")
        batch_result = self.agent.execute_batch_gemini(gemini_dataset)
        
        if batch_result.get("error") or not batch_result.get("analyses"):
            logger.error(f"Gemini Batch failed: {batch_result.get('error', 'No analyses returned')}")
            return {"prediction_ids": [], "candidate_summary": [], "fatal_error": "Gemini batch failed"}
            
        selected_candidates = batch_result.get("selected_candidates", [])
        if not selected_candidates:
            logger.warning("No selected candidates returned by Gemini.")
            return {"prediction_ids": [], "candidate_summary": [], "fatal_error": "No candidates selected"}
        
        # 5. Tavily & Claude & Consensus (Selected Candidates Only)
        for candidate in selected_candidates:
            ticker = candidate["ticker"]
            
            # Gemini 결과 추출
            gemini_analysis = next((a for a in batch_result.get("analyses", []) if a["ticker"] == ticker), None)
            if not gemini_analysis:
                logger.warning(f"Analysis missing for {ticker}, skipping.")
                candidate_summary.append({
                    "ticker": ticker,
                    "status": "FAILED",
                    "consensus_method": "gemini_analysis_missing"
                })
                continue

            # Traceability
            timestamp = datetime.now().isoformat()
            prediction_id = self.db.save_prediction(
                ticker, "PENDING", 0.0, 0.0, "Multi-AI Pending", timestamp
            )
            prediction_ids.append(prediction_id)
            
            # Tavily Search
            search_results = []
            is_tavily_failed = False
            status, results = self.agent.tavily_provider.search(f"{ticker} 최신 뉴스")
            if status == APIStatus.SUCCESS:
                search_results.extend(results)
            else:
                is_tavily_failed = True

            # Claude Analysis & Consensus
            decision_result = self.agent.execute_single(
                market_data=next((d for d in gemini_dataset if d["ticker"] == ticker), {}),
                gemini_analysis=gemini_analysis,
                search_results=search_results,
                prediction_id=prediction_id
            )
            
            is_fallback = decision_result.get("is_fallback", False) if decision_result else True
            method = decision_result.get("consensus", {}).get("method", "fallback_hold") if decision_result else "fallback_hold"
            
            if is_fallback:
                cand_status = "FALLBACK"
            elif is_tavily_failed:
                cand_status = "PARTIAL"
            else:
                cand_status = "SUCCESS"
            
            # 6. PositionSizer & PortfolioManager Execution
            current_price = next((d for d in gemini_dataset if d["ticker"] == ticker), {}).get("price_data", {}).get("current", 0)
            
            if decision_result:
                try:
                    self.portfolio_manager.execute_decision(
                        ticker,
                        decision_result,
                        current_price,
                        prediction_id=prediction_id,
                        market_df=self.market_pipeline.last_market_data
                    )
                except Exception as e:
                    logger.error(f"Portfolio execution failed for {ticker}: {e}")
                    if cand_status != "FALLBACK":
                        cand_status = "PARTIAL"

            candidate_summary.append({
                "ticker": ticker,
                "status": cand_status,
                "consensus_method": method
            })

        return {
            "prediction_ids": prediction_ids,
            "candidate_summary": candidate_summary
        }

    async def _run_mock_cycle(self, market_condition=None) -> dict:
        """
        신규 Gemini 파이프라인 기반 MOCK 테스트 파이프라인
        """
        prediction_ids = []
        candidate_summary = []

        if market_condition:
            self.market_simulator.set_condition(market_condition)
        self.market_simulator.simulate_step()
        
        # 1. Screening & Refinement
        try:
            candidates_df = self.market_pipeline.run()
            refined_df = self.refiner.refine(candidates_df)
        except Exception as e:
            logger.error(f"Mock Market Pipeline failed: {e}")
            return {"prediction_ids": [], "candidate_summary": [], "fatal_error": str(e)}

        if refined_df.empty:
            return {"prediction_ids": [], "candidate_summary": [], "fatal_error": "No candidates"}
        
        # 2. Convert to JSON/Dict
        portfolio_state = self.portfolio_manager.get_current_state()
        self.macro_manager.fetch_and_save_macro_data()
        macro_data = self.macro_manager.get_current_macro_indicators()
        
        market_data_list = self.market_data_adapter.convert_candidates(
            refined_df,
            portfolio_state=portfolio_state,
            macro_data=macro_data
        )
        
        # 3. Iterate over refined candidates
        for market_data in market_data_list:
            target_ticker = market_data["ticker"]
            
            logger.info(f"Executing Multi-AI Pipeline for {target_ticker}")
            
            # Prediction ID (Traceability)
            timestamp = datetime.now().isoformat()
            prediction_id = self.db.save_prediction(
                target_ticker, "PENDING", 0.0, 0.0, "Multi-AI Pending", timestamp
            )
            prediction_ids.append(prediction_id)
            
            # Execute
            decision_result = self.agent.execute(market_data, prediction_id)
            is_fallback = decision_result.get("is_fallback", False) if decision_result else True
            method = decision_result.get("consensus", {}).get("method", "fallback_hold") if decision_result else "fallback_hold"
            cand_status = "FALLBACK" if is_fallback else "SUCCESS"
            
            # Portfolio execution logic (holding over from original)
            current_price = market_data["price_data"]["current"]
            
            if decision_result:
                try:
                    self.portfolio_manager.execute_decision(
                        target_ticker,
                        decision_result,
                        current_price,
                        prediction_id=prediction_id,
                        market_df=self.market_pipeline.last_market_data
                    )
                except Exception as e:
                    logger.error(f"Portfolio execution failed for {target_ticker}: {e}")
                    if cand_status != "FALLBACK":
                        cand_status = "PARTIAL"

            candidate_summary.append({
                "ticker": target_ticker,
                "status": cand_status,
                "consensus_method": method
            })

        return {
            "prediction_ids": prediction_ids,
            "candidate_summary": candidate_summary
        }

    async def _run_adapter_validation(self):
        """
        MarketDataAdapter 변환 결과 및 GPT 입력 구조 검증.
        """
        logger.info("Running ADAPTER VALIDATION mode...")

        # 1. Pipeline 실행
        candidates = self.market_pipeline.run()
        if candidates.empty:
            logger.error("[ERROR] No validated candidates found. Adapter validation skipped.")
            return

        # 로그 출력
        logger.info("=" * 40)
        logger.info("MARKET PIPELINE RESULT")
        logger.info("=" * 20)
        logger.info(f"Candidate Count : {len(candidates)}")
        logger.info(f"Columns: {list(candidates.columns)}")
        logger.info("Candidate Preview:")
        for i, row in candidates.head(5).iterrows():
            logger.info(f"{i+1}. {row.get('ticker')} / {row.get('name')} / {row.get('market')}")
        logger.info("=" * 40)

        # 2. 데이터 변환
        portfolio_state = self.portfolio_manager.get_current_state()
        self.macro_manager.fetch_and_save_macro_data()
        macro_data = self.macro_manager.get_current_macro_indicators()
        
        market_data_list = self.market_data_adapter.convert_candidates(
            candidates,
            portfolio_state=portfolio_state,
            macro_data=macro_data
        )

        # 3. 검증
        logger.info("=" * 40)
        logger.info("ADAPTER OUTPUT VALIDATION")
        logger.info("=" * 20)
        logger.info(f"Pipeline Candidates : {len(candidates)}")
        logger.info(f"Adapter Outputs     : {len(market_data_list)}")
        
        if len(candidates) != len(market_data_list):
            logger.error("Candidate Count Check: FAIL")
        else:
            logger.info("Candidate Count Check: PASS")

        # 필수 필드 검증
        required_fields = ["ticker", "name", "market", "market_data", "portfolio", "macro_data"]
        all_passed = True
        
        for data in market_data_list:
            missing = [f for f in required_fields if f not in data]
            if missing:
                logger.error(f"GPT input validation failed for Ticker: {data.get('ticker')}")
                logger.error(f"Missing Fields: {missing}")
                all_passed = False
        
        logger.info(f"GPT Input Validation: {'PASS' if all_passed else 'FAIL'}")

        # JSON / Type 검증
        json_passed = True
        type_passed = True
        
        for data in market_data_list:
            ticker = data.get("ticker")
            try:
                json_str = json.dumps(data, ensure_ascii=False)
            except Exception as e:
                logger.error(f"JSON serialization failed for {ticker}: {e}")
                json_passed = False
            
            type_errors = self.market_data_adapter.validate_types(data)
            if type_errors:
                logger.error(f"Data type validation failed for {ticker}: {type_errors}")
                type_passed = False
        
        logger.info(f"JSON Serialization: {'PASS' if json_passed else 'FAIL'}")
        logger.info(f"Data Type Validation: {'PASS' if type_passed else 'FAIL'}")
        
        logger.info("OpenAI API Called: NO")
        logger.info("Claude API Called: NO")
        logger.info("=" * 40)
        logger.info("ADAPTER VALIDATION COMPLETED")
        logger.info("=" * 28)



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