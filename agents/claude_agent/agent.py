import json
import logging
from agents.base_agent import BaseTradingAgent
from runtime.tool_manager.anthropic_client import AnthropicClient

logger = logging.getLogger("ClaudeAgent")

class ClaudeAgent(BaseTradingAgent):
    def __init__(self):
        self.client = AnthropicClient()
        self.system_prompt = (
            "You are a professional financial trading assistant and risk validator. "
            "Your task is to evaluate the trading decision made by another AI (GPT). "
            "You must analyze the original market data and the GPT's analysis, then "
            "provide an evaluation in JSON format with the following fields: "
            "evaluation (PASS, WARNING, or REJECT), score (0-100), reasoning (str), "
            "issues (list), risk_level (LOW, MEDIUM, HIGH)."
        )

    def make_decision(self, market_data: dict, gpt_result: dict) -> dict:
        """
        Analyze the given market data and make a trading decision using Claude API.
        """
        user_prompt = (
            f"Original Market Data: {json.dumps(market_data)}\n\n"
            f"GPT's Decision: {json.dumps(gpt_result)}\n\n"
            "Evaluate GPT's decision, logic, and risk assessment. "
            "Return the evaluation in structured JSON format."
        )

        status, response_text = self.client.get_completion(self.system_prompt, user_prompt)

        if status.value != "SUCCESS" or not response_text:
            return None

        try:
            # Basic parsing, handling potential markdown blocks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)

            # Validation
            required = ["evaluation", "score", "reasoning", "issues", "risk_level"]
            if not all(k in data for k in required):
                logger.error("Claude returned incomplete evaluation structure.")
                return None

            return data

        except json.JSONDecodeError:
            logger.error("Failed to parse Claude response as JSON.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing Claude response: {e}")
            return None

