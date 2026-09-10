from abc import ABC, abstractmethod
from typing import List, Optional
from runtime.tool_manager.web_search_client import SearchResult
from runtime.tool_manager.api_error_handler import APIStatus

class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, category: Optional[str] = None) -> tuple[APIStatus, List[SearchResult]]:
        """
        검색을 수행하고 정규화된 SearchResult 리스트를 반환합니다.
        """
        pass
