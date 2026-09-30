import logging
from typing import List, Any
from datetime import datetime
from unittest.mock import MagicMock
from agents.gemini_agent.agent import GeminiAgent
# from agents.gpt_agent.agent import GPTAgent
from agents.claude_agent.agent import ClaudeAgent
from agents.multi_ai.consensus_manager import ConsensusManager
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from runtime.tool_manager.api_error_handler import APIStatus

logger = logging.getLogger("MultiAIOrchestrator")

class MultiAIOrchestrator:
    def __init__(self, db_manager):
        # Restore GPTAgent reference for backward compatibility with tests
        self.gpt_agent = MagicMock() 
        self.gemini_agent = GeminiAgent()
        self.claude_agent = ClaudeAgent()
        self.consensus_manager = ConsensusManager()
        self.tavily_provider = TavilySearchProvider()
        self.db = db_manager

    def _build_search_query(self, ticker: str, name: str, gemini_analysis: dict) -> str:
        """
        Gemini 분석 기반 검색어 생성.
        """
        keywords = []
        analysis = gemini_analysis.get("analysis", {})
        
        # 분석 키워드 추출
        if isinstance(analysis, dict):
            keywords.extend([str(v) for v in analysis.values() if isinstance(v, str)])
        
        # Reasoning 키워드 추가
        reasoning = gemini_analysis.get("reasoning", "")
        if "실적" in reasoning: keywords.append("실적")
        if "수급" in reasoning or "외국인" in reasoning or "기관" in reasoning: keywords.append("수급")
        
        query_parts = [f"{name} ({ticker})"]
        query_parts.extend(keywords[:3]) # 최대 3개 키워드 제한
        query_parts.append("최신 뉴스")
        
        return " ".join(query_parts)

    def _filter_news(self, ticker: str, name: str, search_results: List[Any], gemini_analysis: dict) -> List[Any]:
        """
        뉴스 관련성 필터링 및 중복 제거.
        처리 순서:
        1. 관련성 및 Score 필터
        2. URL 중복 제거
        3. Title 중복 제거
        4. 정렬 (Score/Relevance 및 최신성 기준)
        5. 최대 3개 선별
        """
        if not search_results:
            return []
        
        filtered = []
        for res in search_results:
            score = getattr(res, 'score', getattr(res, 'relevance', 0.5))
            if score is None:
                score = 0.5
            content_lower = (f"{getattr(res, 'title', '')} {getattr(res, 'snippet', '')}").lower()

            # 종목 관련성
            is_relevant = ticker.lower() in content_lower or name.lower() in content_lower

            # 필터링 조건: 점수 > 0.4 또는 종목 관련성 있음
            if score > 0.4 or is_relevant:
                filtered.append(res)
        
        # URL 중복 제거 (동일 URL 1개만 유지)
        seen_urls = set()
        url_deduped = []
        for res in filtered:
            url = getattr(res, 'url', None)
            if url:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
            url_deduped.append(res)

        # Title 중복 제거 (동일 Title 1개만 유지)
        seen_titles = set()
        title_deduped = []
        for res in url_deduped:
            title = getattr(res, 'title', None)
            if title:
                if title in seen_titles:
                    continue
                seen_titles.add(title)
            title_deduped.append(res)

        # 정렬: score/relevance 기준 내림차순, published_at 기준 내림차순(최신순) 보조 정렬
        def sort_key(x):
            s = getattr(x, 'score', getattr(x, 'relevance', 0))
            if s is None: s = 0
            pub = getattr(x, 'published_at', '') or ''
            return (s, pub)

        sorted_results = sorted(title_deduped, key=sort_key, reverse=True)

        # 최대 3개 선별
        return sorted_results[:3]

    def execute(self, market_data: dict, prediction_id: int) -> dict:
        """
        Legacy execute method for backward compatibility.
        """
        # Wrap market_data in list to use the new logic
        gemini_result = self.execute_batch_gemini([market_data])
        
        # Extract analysis for this specific ticker
        ticker = market_data.get("ticker")
        gemini_analysis = next((a for a in gemini_result.get("analyses", []) if a["ticker"] == ticker), None)
        
        # News Search & Filter
        search_results = []
        if gemini_analysis:
            ticker = market_data.get("ticker", "N/A")
            name = market_data.get("name", "N/A")
            
            # Query 생성
            query = self._build_search_query(ticker, name, gemini_analysis)
            logger.info(f"Tavily Query for {ticker}: {query}")
            
            # 검색
            status, results = self.tavily_provider.search(query, max_results=10)
            
            # 필터링
            if status == APIStatus.SUCCESS:
                search_results = self._filter_news(ticker, name, results, gemini_analysis)
                logger.info(f"Search candidates: {len(results)}, Passed filter: {len(search_results)}")
                for i, res in enumerate(search_results):
                    logger.debug(f"News {i}: {res.title}, Score: {getattr(res, 'score', 'N/A')}")
            else:
                logger.warning(f"Tavily search failed for {ticker}")
                
        # Claude Analysis & Consensus
        return self.execute_single(market_data, gemini_analysis, search_results, prediction_id)

    def execute_batch_gemini(self, market_data_list: List[dict]) -> dict:
        """
        Gemini 1차 분석을 Batch로 일괄 수행.
        """
        # 1. Execute Gemini (Analyst) Batch
        try:
            gemini_result = self.gemini_agent.execute_batch(market_data_list)
        except Exception as e:
            logger.error(f"Error executing GeminiAgent.execute_batch: {e}")
            gemini_result = {"analyses": [], "selected_candidates": []}

        # [FIX] Check for consistency between selected_candidates and analyses
        selected = gemini_result.get("selected_candidates", [])
        analyses = gemini_result.get("analyses", [])
        analyzed_tickers = {a["ticker"] for a in analyses if "ticker" in a}

        for candidate in selected:
            ticker = candidate.get("ticker")
            if ticker and ticker not in analyzed_tickers:
                logger.warning(f"Data Mismatch: Candidate {ticker} selected but no analysis found in Gemini output.")

        return gemini_result
    def execute_single(self, market_data: dict, gemini_analysis: dict, search_results: List[Any], prediction_id: int) -> dict:
        """
        이미 분석된 Gemini 결과(single)를 바탕으로 Claude 2차 분석 수행.
        """
        timestamp = datetime.now().isoformat()
        
        # 1. Execute Claude (Evaluator)
        try:
            claude_result = self.claude_agent.make_decision(market_data, gemini_analysis, search_results=search_results)
        except Exception as e:
            logger.error(f"Error executing ClaudeAgent: {e}")
            claude_result = None
            
        # 2. Save Claude evaluation
        self._save_agent_result(prediction_id, timestamp, "claude", claude_result)
            
        # 3. Consensus (Validator)
        final_decision = self.consensus_manager.get_consensus(gemini_analysis, claude_result)
        
        # 4. Construct Final Result
        is_fallback = (final_decision.get("method") == "fallback_hold")
        final_result = {
            "decision": final_decision["decision"],
            "confidence": final_decision["confidence"],
            "reasoning": final_decision["reasoning"],
            "risks": gemini_analysis["risks"] if gemini_analysis else "No Gemini risks",
            "expected_result": gemini_analysis["expected_result"] if gemini_analysis else "No Gemini expected result",
            "is_fallback": is_fallback,
            "consensus": {
                "method": final_decision["method"],
                "participants": ["gemini", "claude"]
            },
            "agent_results": {
                "gemini": gemini_analysis,
                "claude": claude_result
            }
        }
        return final_result

    def _save_agent_result(self, prediction_id, timestamp, model_name, result):
        if not result:
            self.db.save_agent_decision(prediction_id, timestamp, model_name, "ERROR", 0.0, "Failed to get decision", "None")
            return

        # Map to agent_decisions schema
        if model_name == "gpt":
            self.db.save_agent_decision(
                prediction_id, timestamp, model_name, result["decision"], 
                result["confidence"], result["reasoning"], str(result["risks"])
            )
        else: # Claude (Evaluation)
            # Use safe get to avoid KeyError if structure is unexpected
            decision = result.get("evaluation", "ERROR")
            score = result.get("score", 0.0) / 100.0
            reasoning = result.get("reasoning", "No reasoning provided")
            risks = str(result.get("issues", "[]"))
            
            self.db.save_agent_decision(
                prediction_id, timestamp, model_name, decision, 
                score, reasoning, risks
            )
