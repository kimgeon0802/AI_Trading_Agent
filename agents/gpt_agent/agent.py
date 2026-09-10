import os
from agents.base_agent import BaseTradingAgent
from runtime.tool_manager.openai_client import OpenAIClient
from runtime.tool_manager.parser import ResponseParser
from runtime.tool_manager.web_search_client import SearchResult
from typing import List
import json

class GPTAgent(BaseTradingAgent):
    def __init__(self, system_prompt_path="prompts/system_prompt.md", decision_prompt_path="prompts/decision_prompt.md"):
        self.client = OpenAIClient()
        self.system_prompt = self._load_prompt(system_prompt_path)
        self.decision_prompt = self._load_prompt(decision_prompt_path)

    def _load_prompt(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _format_web_search_context(self, results: List[SearchResult]) -> str:
        if not results:
            return ""
        
        context = "\n[Web Search Context]\n\n"
        for res in results:
            context += f"Category: {res.category or 'N/A'}\n"
            if res.title: context += f"Title: {res.title}\n"
            if res.url: context += f"URL: {res.url}\n"
            if res.source: context += f"Source: {res.source}\n"
            if res.published_at: context += f"Published At: {res.published_at}\n"
            if res.snippet: context += f"Snippet: {res.snippet}\n"
            context += "\n"
        
        context += """
Web Search Context는 외부 검색 결과로 제공된 정보입니다.

검색 결과에 존재하지 않는 뉴스, 수치, 날짜, 출처, URL, 기업 이벤트를 임의로 생성하지 마십시오.

검색 결과와 Market Data가 일치하지 않는 경우 각각의 근거를 구분하여 판단하십시오.

검색 결과가 없거나 부족한 경우 해당 사실을 명시하고 Market Data를 기반으로 분석하십시오.

검색 결과만으로 확인되지 않은 사실을 확정적으로 표현하지 마십시오.
"""
        return context

    def make_decision(self, market_data, web_search_results: List[SearchResult] = None):
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

        # Inject Web Search Context
        web_search_str = self._format_web_search_context(web_search_results or [])
        user_prompt += web_search_str

        user_prompt = f"{user_prompt}\n\n# Market Data\n{json.dumps(market_data, indent=2, ensure_ascii=False)}"

        status, response_text = self.client.get_completion(self.system_prompt, user_prompt)
        if status.value == "SUCCESS" and response_text:
            return ResponseParser.parse_decision(response_text)
        return None
