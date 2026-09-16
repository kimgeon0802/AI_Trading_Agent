import pytest
from agents.claude_agent.parser import ClaudeParser

def test_pure_json():
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(json_str) is not None

def test_markdown_json():
    json_str = '```json\n{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": [], "risk_level": "LOW"}\n```'
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
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason"'
    assert ClaudeParser.parse_response(json_str) is None

def test_missing_required_field():
    json_str = '{"evaluation": "PASS", "score": 80, "reasoning": "Reason", "issues": []}'
    assert ClaudeParser.parse_response(json_str) is None
