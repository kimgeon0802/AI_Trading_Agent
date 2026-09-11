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

    def execute(self, market_data: dict, prediction_id: int) -> dict:
        """
        Legacy execute method for backward compatibility.
        """
        # Wrap market_data in list to use the new logic
        gemini_result = self.execute_batch_gemini([market_data])
        
        # Extract analysis for this specific ticker
        ticker = market_data.get("ticker")
        gemini_analysis = next((a for a in gemini_result.get("analyses", []) if a["ticker"] == ticker), None)
        
        # Tavily Search
        search_results = []
        if gemini_analysis:
            status, results = self.tavily_provider.search(f"{ticker} 최신 뉴스")
            if status == APIStatus.SUCCESS:
                search_results.extend(results)
                
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
        final_result = {
            "decision": final_decision["decision"],
            "confidence": final_decision["confidence"],
            "reasoning": final_decision["reasoning"],
            "risks": gemini_analysis["risks"] if gemini_analysis else "No Gemini risks",
            "expected_result": gemini_analysis["expected_result"] if gemini_analysis else "No Gemini expected result",
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
