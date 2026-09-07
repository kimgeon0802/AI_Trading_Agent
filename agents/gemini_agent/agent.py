
from agents.base_agent import BaseTradingAgent
import random

class GeminiMockAgent(BaseTradingAgent):
    def __init__(self):
        pass

    def make_decision(self, market_data: dict) -> dict:
        """
        Mock decision logic based on market data.
        """
        # Simple Mock Logic
        condition = market_data.get("market_summary", {}).get("condition", "neutral")
        
        # Decide based on condition
        if condition == "bullish":
            decision = "BUY"
            confidence = 0.7 + random.uniform(0, 0.2)
            reasoning = "Market condition is bullish, indicating strong upward potential."
            risks = "Market overheating risk, potential for short-term correction."
        elif condition == "bearish":
            decision = "SELL"
            confidence = 0.6 + random.uniform(0, 0.2)
            reasoning = "Market condition is bearish, suggesting downside risk."
            risks = "Risk of missing a recovery, potential for bottom-fishing opportunities."
        else:
            decision = "HOLD"
            confidence = 0.8 + random.uniform(0, 0.1)
            reasoning = "Market condition is neutral; cautious approach recommended."
            risks = "Stagnation risk, opportunity cost of capital."
        
        return {
            "decision": decision,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "risks": risks,
            "expected_result": f"Expected {decision} outcome based on {condition} market."
        }
