import os
import pytest
import logging
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from runtime.tool_manager.api_error_handler import APIStatus
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Real 테스트를 위해 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRealTavily")

@pytest.mark.skipif(os.getenv("RUN_REAL_TESTS") != "true", reason="Real tests disabled")
def test_real_tavily_search():
    # Real 모드 활성화 및 안전장치
    os.environ["USE_MOCK_AI"] = "false"
    
    # 설정 검증
    if os.getenv("TAVILY_API_KEY") is None:
        pytest.skip("TAVILY_API_KEY not set")

    # 0. Setup (Real Client)
    provider = TavilySearchProvider()
    
    # Query
    query = "SK하이닉스 최신 뉴스"
    
    # 1. Tavily 검색 호출 (1회만 호출)
    logger.info(f"Tavily API Attempt #1: {query}")
    status, results = provider.search(query, category="news")
    
    # 2. Verify
    assert status == APIStatus.SUCCESS
    assert results is not None
    assert len(results) > 0
    
    result = results[0]
    logger.info(f"Search Result: title={result.title}, url={result.url}")
    
    assert result.title is not None
    assert result.url is not None
    assert result.snippet is not None
    
    logger.info("Tavily search passed.")
