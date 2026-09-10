import logging
from agents.gemini_agent.agent import GeminiAgent
# from agents.gpt_agent.agent import GPTAgent
from agents.claude_agent.agent import ClaudeAgent
from agents.multi_ai.consensus_manager import ConsensusManager

logger = logging.getLogger("MultiAIOrchestrator")

class MultiAIOrchestrator:
    def __init__(self, db_manager):
        # self.gpt_agent = GPTAgent()
        self.gemini_agent = GeminiAgent()
        self.claude_agent = ClaudeAgent()
        self.consensus_manager = ConsensusManager()
        self.db = db_manager

    def execute(self, market_data: dict, prediction_id: int) -> dict:
        """
        Orchestrate sequential decision making: Gemini -> Claude -> Consensus.
        """
        timestamp = market_data["timestamp"]
        
        # 1. Execute Gemini (Analyst)
        try:
            # gpt_result = self.gpt_agent.make_decision(market_data)
            gemini_result = self.gemini_agent.make_decision(market_data)
        except Exception as e:
            logger.error(f"Error executing GeminiAgent: {e}")
            gemini_result = None
        
        # Save Gemini decision (사용자 DB 스키마에 따라 'gpt' 레이블 유지 또는 변경)
        self._save_agent_result(prediction_id, timestamp, "gpt", gemini_result)
            
        # 2. Execute Claude (Evaluator)
        claude_result = None
        if gemini_result:
            try:
                # Claude receives Gemini result for evaluation
                claude_result = self.claude_agent.make_decision(market_data, gemini_result)
            except Exception as e:
                logger.error(f"Error executing ClaudeAgent: {e}")
        else:
            logger.warning("Skipping Claude evaluation due to Gemini failure.")
            
        # Save Claude evaluation
        self._save_agent_result(prediction_id, timestamp, "claude", claude_result)
            
        # 3. Consensus (Validator)
        final_decision = self.consensus_manager.get_consensus(gemini_result, claude_result)
        
        # 4. Construct Final Result
        final_result = {
            "decision": final_decision["decision"],
            "confidence": final_decision["confidence"],
            "reasoning": final_decision["reasoning"],
            "risks": gemini_result["risks"] if gemini_result else "No Gemini risks",
            "expected_result": gemini_result["expected_result"] if gemini_result else "No Gemini expected result",
            "consensus": {
                "method": final_decision["method"],
                "participants": ["gemini", "claude"]
            },
            "agent_results": {
                "gemini": gemini_result,
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
