
from agents.base_agent import BaseTradingAgent
import random

class ClaudeMockAgent(BaseTradingAgent):
    def __init__(self):
        pass

    def make_decision(self, market_data: dict) -> dict:
        """
        Mock decision logic based on market data, distinct from GeminiMockAgent.
        """
        # Claude focuses more on sentiment and risk
        sentiment = market_data.get("sentiment_analysis", {}).get("score", 0) # Assumed range -1 to 1
        risk = market_data.get("risk_report", {}).get("risk_level", "medium")
        
        # Claude's decision logic:
        # Sentiment > 0.2 and risk <= medium -> BUY
        # Sentiment < -0.2 or risk == high -> SELL
        # Otherwise -> HOLD
        
        if sentiment > 0.2 and risk != "high":
            decision = "BUY"
            confidence = 0.65 + random.uniform(0, 0.25)
            reasoning = "Claude Sentiment Analysis indicates bullish sentiment and acceptable risk levels."
            risks = f"Market volatility might impact execution. Risk level reported: {risk}."
        elif sentiment < -0.2 or risk == "high":
            decision = "SELL"
            confidence = 0.7 + random.uniform(0, 0.2)
            reasoning = "Claude Sentiment Analysis indicates bearish sentiment or high market risk."
            risks = f"Potential downside risk. Risk level reported: {risk}."
        else:
            decision = "HOLD"
            confidence = 0.75 + random.uniform(0, 0.15)
            reasoning = "Claude Sentiment Analysis is neutral, no clear trend."
            risks = "Uncertain market direction."
        
        return {
            "decision": decision,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "risks": risks,
            "expected_result": f"Expected {decision} outcome based on Claude's sentiment analysis."
        }
