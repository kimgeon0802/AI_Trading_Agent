import json
import logging
from agents.base_agent import BaseTradingAgent
from runtime.tool_manager.anthropic_client import AnthropicClient

logger = logging.getLogger("ClaudeAgent")

class ClaudeAgent(BaseTradingAgent):
    def __init__(self):
        self.client = AnthropicClient()
        self.system_prompt = "You are a professional financial trading assistant. Provide responses in JSON format."

    def make_decision(self, market_data: dict) -> dict:
        """
        Analyze the given market data and make a trading decision using Claude API.
        """
        user_prompt = f"Analyze the following market data and provide a trading decision: {json.dumps(market_data)}"
        
        response_text = self.client.get_completion(self.system_prompt, user_prompt)
        
        if not response_text:
            return None
            
        try:
            # Basic parsing, handling potential markdown blocks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
            # Validation
            required = ["decision", "confidence", "reasoning", "risks", "expected_result"]
            if not all(k in data for k in required):
                logger.error("Claude returned incomplete JSON structure.")
                return None
            
            return data
            
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude response as JSON.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing Claude response: {e}")
            return None
