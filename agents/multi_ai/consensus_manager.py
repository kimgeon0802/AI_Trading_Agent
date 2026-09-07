import logging
from collections import Counter

# Configure logging
logger = logging.getLogger("ConsensusManager")

class ConsensusManager:
    @staticmethod
    def get_consensus(agent_results: dict) -> dict:
        """
        Synthesize decisions from GPT and Claude agents based on consensus rules.
        
        agent_results expected structure:
        {
            "gpt": {...},
            "claude": {...}
        }
        """
        valid_results = {}
        for agent_name, result in agent_results.items():
            if ConsensusManager._is_valid(result):
                valid_results[agent_name] = result
        
        participating_agents = list(valid_results.keys())
        
        if not valid_results:
            return ConsensusManager._fallback_hold("All agents failed or returned invalid results.")
        
        # 1. Check for Agreement
        if len(valid_results) == 2:
            decisions = [res["decision"] for res in valid_results.values()]
            if decisions[0] == decisions[1]:
                # GPT and Claude agree
                res = list(valid_results.values())[0]
                return {
                    "decision": decisions[0],
                    "confidence": (valid_results["gpt"]["confidence"] + valid_results["claude"]["confidence"]) / 2,
                    "reasoning": f"Consensus between GPT and Claude: {res['reasoning']}",
                    "consensus_type": "agreement",
                    "participating_agents": participating_agents,
                    "agent_results": valid_results
                }
        
        # 2. Confidence Resolution / Partial Failure
        # Select result with highest confidence among valid results
        best_result = max(valid_results.values(), key=lambda x: x["confidence"])
        
        return {
            "decision": best_result["decision"],
            "confidence": best_result["confidence"],
            "reasoning": best_result["reasoning"],
            "consensus_type": "confidence_resolution",
            "participating_agents": participating_agents,
            "agent_results": valid_results
        }

    @staticmethod
    def _is_valid(result: dict) -> bool:
        if not isinstance(result, dict):
            return False
        required_fields = ["decision", "confidence", "reasoning", "risks", "expected_result"]
        return all(field in result for field in required_fields) and result["decision"] in ["BUY", "SELL", "HOLD"]

    @staticmethod
    def _fallback_hold(reason: str) -> dict:
        logger.warning(f"Consensus Fallback: {reason}")
        return {
            "decision": "HOLD",
            "confidence": 0.0,
            "reasoning": f"Fallback due to: {reason}",
            "consensus_type": "fallback_hold",
            "participating_agents": [],
            "agent_results": {}
        }
