import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from tavily import TavilyClient
from runtime.tool_manager.search_provider import SearchProvider
from runtime.tool_manager.web_search_client import SearchResult
from runtime.tool_manager.api_error_handler import APIStatus, classify_error

# 환경변수 로드
load_dotenv()

logger = logging.getLogger("TavilySearchProvider")

class TavilySearchProvider(SearchProvider):
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
        self.api_key = os.getenv("TAVILY_API_KEY")
        
        if not self.use_mock:
            if not self.api_key:
                raise ValueError("TAVILY_API_KEY not found")
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def search(self, query: str, category: Optional[str] = None) -> tuple[APIStatus, List[SearchResult]]:
        if self.use_mock:
            return APIStatus.SUCCESS, self._get_mock_results(query, category)
        
        try:
            # Tavily 검색 호출 (실제 API 호출)
            response = self.client.search(query=query, search_depth="advanced")
            return APIStatus.SUCCESS, self._normalize_response(response, query, category)
            
        except Exception as e:
            status = classify_error(e)
            logger.error(f"Tavily Search Error ({status}): query={query}, error={e}")
            return status, []

    def _normalize_response(self, response: dict, query: str, category: Optional[str] = None) -> List[SearchResult]:
        results = []
        if not response or "results" not in response:
            return results
        
        for item in response["results"]:
            results.append(SearchResult(
                query=query,
                category=category,
                title=item.get("title"),
                url=item.get("url"),
                snippet=item.get("content"),
                published_at=item.get("published_date")
            ))
        return results

    def _get_mock_results(self, query: str, category: Optional[str] = None) -> List[SearchResult]:
        return [
            SearchResult(
                query=query,
                category=category,
                title=f"Mock Tavily Title for {query}",
                url="https://tavily.mock.example.com",
                snippet=f"Mock Tavily content for: {query}"
            )
        ]
