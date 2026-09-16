import pytest
from agents.claude_agent.parser import ClaudeParser

def test_claude_parser_robustness():
    # 1. Normal
    normal_json = '{"evaluation": "PASS", "score": 90, "reasoning": "Good", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(normal_json) is not None

    # 2. Nested objects
    nested_json = '{"evaluation": "PASS", "score": 90, "reasoning": "Good", "issues": [], "risk_level": "LOW", "nested": {"a": 1}}'
    assert ClaudeParser.parse_response(nested_json) is not None

    # 3. With Markdown Code Fence
    fenced_json = 'Some text here\n```json\n{"evaluation": "PASS", "score": 90, "reasoning": "Good", "issues": [], "risk_level": "LOW"}\n```\nMore text'
    assert ClaudeParser.parse_response(fenced_json) is not None
    
    # 4. Nested in Fence
    fenced_nested_json = '```json\n{"evaluation": "PASS", "score": 90, "reasoning": "Good", "issues": [], "risk_level": "LOW", "nested": {"a": 1}}\n```'
    assert ClaudeParser.parse_response(fenced_nested_json) is not None

    # 5. Reasoning with braces
    reasoning_braces_json = '{"evaluation": "PASS", "score": 90, "reasoning": "The code {x} works", "issues": [], "risk_level": "LOW"}'
    assert ClaudeParser.parse_response(reasoning_braces_json) is not None
