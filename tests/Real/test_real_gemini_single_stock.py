import os
import pytest
import logging
from agents.gemini_agent.agent import GeminiAgent
from runtime.tool_manager.api_error_handler import APIStatus

# Real 테스트를 위해 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRealGemini")

@pytest.mark.skipif(os.getenv("RUN_REAL_TESTS") != "true", reason="Real tests disabled")
def test_real_gemini_single_stock():
    # Real 모드 활성화 (반드시 USE_MOCK_AI=false)
    os.environ["USE_MOCK_AI"] = "false"
    
    # 설정 검증
    if os.getenv("GEMINI_API_KEY") is None:
        pytest.skip("GEMINI_API_KEY not set")

    # 0. Setup (Real Client)
    agent = GeminiAgent()
    
    # 실제 종목 데이터
    market_data = {
        "name": "SK하이닉스",
        "ticker": "000660",
        "sector": "반도체",
        "market_summary": {"condition": "bullish"},
        "macro_data": {"interest_rate": "3.5%"},
        "timestamp": "2026-09-10"
    }
    
    # 1. GeminiAgent 호출 (1회만 호출 보장)
    logger.info("Executing GeminiAgent.make_decision for SK Hynix")
    decision = agent.make_decision(market_data)
    
    # 2. Verify
    assert decision is not None
    assert "decision" in decision
    assert decision["decision"] in ["BUY", "SELL", "HOLD"]
    
    logger.info(f"Gemini Decision received: {decision}")
