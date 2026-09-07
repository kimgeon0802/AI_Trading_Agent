import logging
from collections import Counter

logger = logging.getLogger("ConsensusManager")

class ConsensusManager:
    @staticmethod
    def get_consensus(gpt_result: dict, claude_result: dict) -> dict:
        """
        Final decision maker based on GPT decision and Claude's evaluation.
        """
        # Fallback if GPT failed
        if not gpt_result:
            return ConsensusManager._fallback_hold("GPT failed, cannot proceed.")

        # If GPT succeeded, check Claude's evaluation
        if not claude_result:
            return ConsensusManager._fallback_hold("Claude failed to evaluate GPT decision.")
        
        evaluation = claude_result["evaluation"]
        
        # Risk Gate Logic
        if evaluation == "PASS":
            return {
                "decision": gpt_result["decision"],
                "confidence": gpt_result["confidence"],
                "reasoning": f"GPT decision validated by Claude: {gpt_result['reasoning']}",
                "method": "validated_by_claude"
            }
        elif evaluation == "WARNING":
            return {
                "decision": "HOLD",
                "confidence": 0.5, # Reduced confidence
                "reasoning": f"Claude issued WARNING: {claude_result['reasoning']}",
                "method": "risk_gate_warning"
            }
        elif evaluation == "REJECT":
            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Claude REJECTED decision: {claude_result['reasoning']}",
                "method": "risk_gate_rejection"
            }
        else:
            return ConsensusManager._fallback_hold(f"Unknown Claude evaluation: {evaluation}")

    @staticmethod
    def _fallback_hold(reason: str) -> dict:
        logger.warning(f"Consensus Fallback: {reason}")
        return {
            "decision": "HOLD",
            "confidence": 0.0,
            "reasoning": f"Fallback due to: {reason}",
            "method": "fallback_hold"
        }
