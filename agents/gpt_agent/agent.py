import os
from agents.base_agent import BaseTradingAgent
from runtime.tool_manager.openai_client import OpenAIClient
from runtime.tool_manager.parser import ResponseParser
import json

class GPTAgent(BaseTradingAgent):
    def __init__(self, system_prompt_path="prompts/system_prompt.md", decision_prompt_path="prompts/decision_prompt.md"):
        self.client = OpenAIClient()
        self.system_prompt = self._load_prompt(system_prompt_path)
        self.decision_prompt = self._load_prompt(decision_prompt_path)

    def _load_prompt(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def make_decision(self, market_data):
        """
        market_data should be a JSON-serializable dictionary containing:
        - market_summary
        - macro_data
        - portfolio
        - news
        - technical_indicators
        """
        
        # Inject Macro Data
        macro_data = market_data.get("macro_data", {})
        macro_str = json.dumps(macro_data, indent=2, ensure_ascii=False) if macro_data else "No current macro data available."
        user_prompt = self.decision_prompt.replace("{{MACRO_DATA}}", macro_str)

        user_prompt = f"{user_prompt}\n\n# Market Data\n{json.dumps(market_data, indent=2, ensure_ascii=False)}"

        status, response_text = self.client.get_completion(self.system_prompt, user_prompt)
        if status.value == "SUCCESS" and response_text:
            return ResponseParser.parse_decision(response_text)
        return None
