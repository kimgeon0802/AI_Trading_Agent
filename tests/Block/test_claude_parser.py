import pytest
from agents.claude_agent.parser import ClaudeParser

def test_parser_normal():
    # 순수 JSON
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Good", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(json_str) is not None
    
    # Fenced JSON
    fenced = '```json\n{"evaluation": "PASS", "score": 80, "reasoning": "Good", "issues": [], "risk_level": "LOW"}\n```'
    assert ClaudeParser.parse_response(fenced) is not None
    
    # 앞뒤 설명 포함
    desc = 'Here is the result: {"evaluation": "PASS", "score": 80, "reasoning": "Good", "issues": [], "risk_level": "LOW"} End.'
    assert ClaudeParser.parse_response(desc) is not None

def test_parser_abnormal():
    # Truncated (incomplete json)
    truncated = '{"evaluation": "PASS", "score": 80'
    assert ClaudeParser.parse_response(truncated) is None
    
    # 필드 누락
    missing_field = '{"evaluation": "PASS", "score": 80}'
    assert ClaudeParser.parse_response(missing_field) is None
    
    # 잘못된 decision
    invalid_decision = '{"evaluation": "UNKNOWN", "score": 80, "reasoning": "Good", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(invalid_decision) is None
    
    # 잘못된 confidence(score) 범위
    invalid_score = '{"evaluation": "PASS", "score": 150, "reasoning": "Good", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(invalid_score) is None
