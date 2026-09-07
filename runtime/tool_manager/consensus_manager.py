import logging
from collections import Counter

logger = logging.getLogger("ConsensusManager")

class ConsensusManager:
    """
    ConsensusManager aggregates decisions from multiple AI agents
    to make a final trading decision.
    """

    def aggregate_decisions(self, agent_results: dict) -> dict:
        """
        agent_results: dict where keys are agent names and values are their decision dicts.
        Example:
        {
            "GPT": {"decision": "BUY", "confidence": 0.8, ...},
            "Gemini": {"decision": "BUY", "confidence": 0.7, ...},
            "Claude": {"decision": "HOLD", "confidence": 0.6, ...}
        }
        """
        # Filter out failed agents
        valid_results = {name: res for name, res in agent_results.items() if res is not None}

        if not valid_results:
            logger.warning("No valid agent results. Falling back to safe HOLD.")
            return self._fallback_hold("No AI agents responded successfully.")

        # 1. Count decisions
        decisions = [res["decision"] for res in valid_results.values()]
        decision_counts = Counter(decisions)
        
        # 2. Check for majority
        # majority_threshold = len(valid_results) / 2
        most_common_decision, count = decision_counts.most_common(1)[0]

        if count > len(valid_results) / 2:
            logger.info(f"Majority decision found: {most_common_decision} ({count}/{len(valid_results)})")
            return self._finalize_decision(most_common_decision, valid_results, "Majority Consensus")

        # 3. No majority - use highest confidence
        logger.info("No majority decision. Selecting by highest confidence.")
        best_agent = max(valid_results, key=lambda x: valid_results[x]["confidence"])
        highest_conf_decision = valid_results[best_agent]["decision"]
        
        return self._finalize_decision(highest_conf_decision, valid_results, f"Highest Confidence ({best_agent})")

    def _finalize_decision(self, final_decision, valid_results, method):
        # Calculate average confidence for the selected decision among agents who agreed
        supporting_agents = [name for name, res in valid_results.items() if res["decision"] == final_decision]
        avg_confidence = sum(valid_results[name]["confidence"] for name in supporting_agents) / len(supporting_agents)
        
        # Combine reasoning
        combined_reasoning = f"Method: {method}\n"
        for name, res in valid_results.items():
            res_text = res['reasoning'] if isinstance(res['reasoning'], str) else " ".join(res['reasoning'])
            combined_reasoning += f"- {name} ({res['decision']}, {res['confidence']}): {res_text}\n"

        # Combine risks
        combined_risks = []
        for name, res in valid_results.items():
            risks = res['risks'] if isinstance(res['risks'], list) else [res['risks']]
            combined_risks.extend([f"[{name}] {r}" for r in risks])

        return {
            "decision": final_decision,
            "confidence": round(avg_confidence, 2),
            "reasoning": combined_reasoning,
            "risks": combined_risks,
            "expected_result": "Consensus reached based on multiple AI analyses.",
            "metadata": {
                "method": method,
                "agents_count": len(valid_results),
                "supporting_agents": supporting_agents
            }
        }

    def _fallback_hold(self, reason):
        return {
            "decision": "HOLD",
            "confidence": 0.0,
            "reasoning": f"Fallback to HOLD: {reason}",
            "risks": ["System failure or no AI response"],
            "expected_result": "Safety first due to lack of AI consensus.",
            "metadata": {"method": "Fallback"}
        }
