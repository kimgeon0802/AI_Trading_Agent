import os
import logging
import json
from dataclasses import dataclass, field
from typing import List, Optional, Union
from openai import OpenAI
from openai.types.responses import WebSearchTool
from runtime.tool_manager.api_error_handler import APIStatus, classify_error

logger = logging.getLogger("WebSearchClient")

@dataclass
class SearchResult:
    query: str
    category: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[str] = None
    snippet: Optional[str] = None
    summary: Optional[str] = None
    relevance: Optional[float] = None

class WebSearchClient:
    """
    WebSearchClient: OpenAI Responses API를 사용하여 웹 검색을 수행합니다.
    
    비용 보호 지침:
    - B9.5 분석에 따르면, 테스트 반복 실행 시 1회 테스트당 5회의 API 호출이 발생하여 비용이 증가함.
    - 이에 따라, Real 환경(USE_MOCK_AI=false)에서 API 호출 횟수를 엄격히 제한함.
    """
    _call_count = 0
    MAX_REAL_CALLS = 5 # 테스트 안전 한도 (1종목 1회 실행 기준)

    def __init__(self, client=None):
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None

        if not self.use_mock and not self.api_key and not is_testing:
            raise ValueError("OPENAI_API_KEY not found and USE_MOCK_AI is false")
        
        if client:
            self.client = client
        elif not self.use_mock:
            self.client = OpenAI(api_key=self.api_key or "dummy")
        else:
            self.client = None

    def search(self, query: str, category: Optional[str] = None) -> tuple[APIStatus, List[SearchResult]]:
        if self.use_mock:
            return APIStatus.SUCCESS, self._get_mock_results(query, category)
        
        # 비용 보호장치: 테스트 환경이 아니고, 실환경 호출 시 횟수 체크
        if not os.getenv("PYTEST_CURRENT_TEST"):
            WebSearchClient._call_count += 1
            if WebSearchClient._call_count > WebSearchClient.MAX_REAL_CALLS:
                logger.error(f"Cost protection: Real API call budget exceeded: {WebSearchClient._call_count}")
                return APIStatus.API_ERROR, []
            
        try:
            web_search_tool = WebSearchTool(type="web_search")
            # attempt 기록
            logger.info(f"Web Search attempt: category={category}, query={query}, total_calls={WebSearchClient._call_count}")
            
            response = self.client.responses.create(
                model=self.model,
                tools=[web_search_tool],
                input=query,
                instructions="주어진 질문에 대해 웹 검색을 수행하고 결과를 정규화하여 반환하세요."
            )
            return APIStatus.SUCCESS, self._normalize_response(response, query, category)
            
        except Exception as e:
            status = classify_error(e)
            logger.error(f"Web Search Error ({status}): category={category}, query={query}, type={type(e).__name__}, error={e}")
            return status, []

    def _normalize_response(self, response, query: str, category: Optional[str] = None) -> List[SearchResult]:
        results = []
        if not response:
            logger.warning(f"Empty response for query: {query}")
            return results
            
        if not hasattr(response, 'output') or response.output is None:
            logger.warning(f"Response has no output or it is None for query: {query}")
            return results
            
        for item in response.output:
            # 디버깅: item 타입 및 속성 확인
            logger.debug(f"Item type: {type(item)}")
            
            # Web Search 관련 응답 항목 확인
            # 'type' 속성
            item_type = getattr(item, 'type', 'N/A')
            logger.debug(f"Item type attribute: {item_type}")
            
            # 검색 호출인 경우 확인
            if item_type == 'web_search_call':
                action = getattr(item, 'action', None)
                if action is not None:
                    logger.debug(f"Action dir: {dir(action)}")
                    sources = getattr(action, 'sources', None)
                    logger.debug(f"Item has action: True, sources: {sources is not None}")
                    
                    if sources is not None:
                        for source in sources:
                            results.append(SearchResult(
                                query=query,
                                category=category,
                                url=getattr(source, 'url', None),
                                title=getattr(source, 'title', None)
                            ))
                else:
                    logger.debug("Item has no action")
        return results

    def _get_mock_results(self, query: str, category: Optional[str] = None) -> List[SearchResult]:
        return [
            SearchResult(
                query=query,
                category=category,
                title=f"Mock Title for {query}",
                url="https://mock.example.com",
                source="Mock Source",
                snippet=f"This is a mock snippet for query: {query}",
                relevance=0.9
            )
        ]
