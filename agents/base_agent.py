from abc import ABC, abstractmethod

class BaseTradingAgent(ABC):
    """
    BaseTradingAgent is the abstract base class for all AI trading agents
    (e.g., GPTAgent, GeminiAgent, ClaudeAgent).
    It defines a common interface that all agents must implement.
    """

    @abstractmethod
    def make_decision(self, market_data: dict) -> dict:
        """
        Analyze the given market data and make a trading decision.

        Args:
            market_data (dict): A dictionary containing:
                - market_summary (dict)
                - macro_data (dict)
                - portfolio (dict)
                - news (list)
                - sentiment_analysis (dict, optional)
                - risk_report (dict, optional)
                - technical_indicators (dict)

        Returns:
            dict: A dictionary containing the following keys (or None if failed):
                - decision (str): "BUY", "SELL", or "HOLD"
                - confidence (float): AI's confidence level
                - reasoning (str): Reasoning for the decision
                - risks (str): Risks associated with the decision
                - expected_result (str): Expected outcome or target of the decision
        """
        pass
