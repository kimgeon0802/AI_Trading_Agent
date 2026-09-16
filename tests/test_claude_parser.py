import pytest
from agents.claude_agent.parser import ClaudeParser

def test_pure_json():
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(json_str) is not None

def test_markdown_json():
    json_str = '```json\n{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": [], "risk_level": "LOW"}\n```'
    assert ClaudeParser.parse_response(json_str) is not None

def test_json_with_trailing_data():
    # Extra data가 있어도 성공해야 함
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": [], "risk_level": "LOW"} 추가 설명'
    assert ClaudeParser.parse_response(json_str) is not None

def test_nested_braces_in_string():
    json_str = '''{
  "evaluation": "PASS",
  "score": 80,
  "reasoning": "Reasoning with {braces} inside",
  "issues": [],
  "risk_level": "LOW"
}'''
    assert ClaudeParser.parse_response(json_str) is not None

def test_malformed_json():
    # 문법 오류는 실패해야 함
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason"'
    assert ClaudeParser.parse_response(json_str) is None

def test_missing_required_field():
    # Schema validation 실패
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": []}'
    assert ClaudeParser.parse_response(json_str) is None
