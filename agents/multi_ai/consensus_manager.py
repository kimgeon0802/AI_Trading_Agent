import logging
from collections import Counter

logger = logging.getLogger("ConsensusManager")

class ConsensusManager:
    @staticmethod
    def get_consensus(analysis_result: dict, claude_result: dict) -> dict:
        """
        Final decision maker based on analysis result and Claude's evaluation.
        """
        # Fallback if analysis failed
        if not analysis_result:
            return ConsensusManager._fallback_hold("1st-stage analysis failed, cannot proceed.")

        # If analysis succeeded, check Claude's evaluation
        if not claude_result:
            return ConsensusManager._fallback_hold("Claude failed to evaluate analysis result.")
        
        evaluation = claude_result["evaluation"]
        
        # Risk Gate Logic
        if evaluation == "PASS":
            return {
                "decision": analysis_result["decision"],
                "confidence": analysis_result["confidence"],
                "reasoning": f"Analysis result validated by Claude: {analysis_result['reasoning']}",
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
