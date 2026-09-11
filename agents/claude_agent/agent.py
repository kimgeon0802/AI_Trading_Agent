import json
import logging
from typing import List, Optional
from agents.base_agent import BaseTradingAgent
from runtime.tool_manager.anthropic_client import AnthropicClient
from rag.rag_engine import RAGEngine
from agents.claude_agent.parser import ClaudeParser

logger = logging.getLogger("ClaudeAgent")

class ClaudeAgent(BaseTradingAgent):
    def __init__(self):
        self.client = AnthropicClient()
        self.system_prompt = (
            "You are a professional financial trading assistant and risk validator. "
            "Your task is to evaluate the trading decision made by another AI (Gemini). "
            "You must analyze the original market data and the Gemini's analysis, then "
            "provide an evaluation in JSON format with the following fields: "
            "evaluation (PASS, WARNING, or REJECT), score (0-100), reasoning (str), "
            "issues (list), risk_level (LOW, MEDIUM, HIGH). "
            "IMPORTANT: Output MUST be a valid JSON object."
        )
        # RAG Engine initialization
        self.rag_engine = RAGEngine()
        try:
            self.rag_engine.load_index()
            self.rag_enabled = True
        except Exception as e:
            logger.error(f"Failed to load RAG index: {e}. RAG will be disabled.")
            self.rag_enabled = False

    def _build_rag_query(self, market_data: dict, gpt_result: dict) -> str:
        """
        Builds a concise, natural language query for RAG retrieval.
        """
        query_parts = [
            f"Stock: {market_data.get('name', 'Unknown')} ({market_data.get('ticker', 'N/A')})",
            f"Market: {market_data.get('market', 'N/A')}"
        ]
        
        # Adjust for new dataset format
        pd = market_data.get("price_data", {})
        signals = [
            f"Price: {pd.get('current', 'N/A')}",
            f"Change: {pd.get('change_rate', 'N/A')}%"
        ]
        query_parts.append(f"Market signals: {', '.join(signals)}")
        
        if gpt_result:
            gpt_parts = [
                f"Decision: {gpt_result.get('decision', 'N/A')}",
                f"Reasoning: {str(gpt_result.get('reasoning', ''))[:100]}"
            ]
            query_parts.append(f"GPT analysis: {', '.join(gpt_parts)}")
        else:
            query_parts.append("GPT analysis: Not available")
            
        query_parts.append("Find relevant investment knowledge about: technical analysis, market risks, valuation, investment strategy.")
        
        return "\n\n".join(query_parts)

    def _format_rag_context(self, results: list) -> str:
        """
        Formats retrieved knowledge documents into a string for the Claude prompt.
        """
        if not results:
            return "No additional relevant investment knowledge retrieved."
        
        context_parts = ["[Relevant Knowledge]"]
        for i, res in enumerate(results, 1):
            context_parts.append(
                f"{i}. Source: {res.metadata.get('source', 'Unknown')}\n"
                f"   Category: {res.metadata.get('category', 'General')}\n"
                f"   Content: {res.page_content.strip()}"
            )
        return "\n\n".join(context_parts)

    def make_decision(self, market_data: dict, gpt_result: dict, search_results: Optional[List] = None) -> dict:
        """
        Analyze the given market data and make a trading decision using Claude API.
        """
        rag_context = "No relevant knowledge retrieved."
        if self.rag_enabled:
            try:
                rag_query = self._build_rag_query(market_data, gpt_result)
                results = self.rag_engine.retrieve(rag_query, top_k=3)
                rag_context = self._format_rag_context(results)
                logger.info(f"[RAG] Retrieved {len(results)} chunks.")
            except Exception as e:
                logger.error(f"[RAG] Retrieval failed: {e}")
        
        # Web Search Context 통합
        search_context = ""
        if search_results:
            search_context = "\n\n[Web Search Results]\n"
            for res in search_results:
                search_context += f"- Title: {res.title}, URL: {res.url}\n"
        
        user_prompt = (
            f"Original Market Data: {json.dumps(market_data)}\n\n"
            f"Gemini's Decision: {json.dumps(gpt_result)}\n\n"
            f"{rag_context}\n"
            f"{search_context}\n\n"
            "Evaluate Gemini's decision, logic, and risk assessment based on market data, Gemini analysis, web search results, and relevant knowledge. "
            "Return the evaluation in structured JSON format."
        )

        status, response_text = self.client.get_completion(self.system_prompt, user_prompt)

        if status.value != "SUCCESS" or not response_text:
            return None

        return ClaudeParser.parse_response(response_text)

