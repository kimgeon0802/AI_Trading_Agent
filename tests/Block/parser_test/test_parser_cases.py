import json
import pytest
from agents.claude_agent.parser import ClaudeParser

def test_parse_response_cases():
    parser = ClaudeParser()

    # Case 1: Raw JSON
    raw_json = '{"evaluation":"PASS","score":90,"reasoning":"Reasoning","issues":[],"risk_level":"LOW"}'
    assert parser.parse_response(raw_json) is not None

    # Case 2: Markdown JSON
    markdown_json = '```json\n{"evaluation":"PASS","score":90,"reasoning":"Reasoning","issues":[],"risk_level":"LOW"}\n```'
    assert parser.parse_response(markdown_json) is not None

    # Case 3: Markdown fence without language
    markdown_no_lang = '```\n{"evaluation":"PASS","score":90,"reasoning":"Reasoning","issues":[],"risk_level":"LOW"}\n```'
    assert parser.parse_response(markdown_no_lang) is not None

    # Case 4: Explanation + Markdown JSON
    explanation_json = 'Here is the evaluation:\n\n```json\n{\n  "evaluation": "WARNING",\n  "score": 62,\n  "reasoning": "Gemini\'s BUY decision shows some...",\n  "issues": [],\n  "risk_level": "MEDIUM"\n}\n```'

    # Case 5: JSON object in middle of text
    mid_text = 'some text\n{"evaluation":"WARNING","score":62,"reasoning":"Reasoning","issues":[],"risk_level":"LOW"}\nsome text'
    assert parser.parse_response(mid_text) is not None

    # Invalid JSON
    assert parser.parse_response('{"invalid": json}') is None

    # Empty response
    assert parser.parse_response('') is None

if __name__ == "__main__":
    pytest.main([__file__])
