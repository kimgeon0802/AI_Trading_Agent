import pytest
from agents.claude_agent.parser import ClaudeParser

def test_nested_json_parsing():
    # Case: Nested JSON
    nested_json = '''
    ```json
    {
      "evaluation": "WARNING",
      "score": 55,
      "reasoning": "...",
      "issues": ["..."],
      "risk_level": "MEDIUM",
      "additional_concerns": {
        "market_context": "...",
        "volatility": "..."
      }
    }
    ```
    '''
    result = ClaudeParser.parse_response(nested_json)
    assert result is not None
    assert result["evaluation"] == "WARNING"
    assert "additional_concerns" in result
    assert result["additional_concerns"]["volatility"] == "..."

def test_deep_nested_json_parsing():
    # Case: Deeply Nested JSON
    deep_json = '''
    {
      "evaluation": "PASS",
      "score": 90,
      "reasoning": "...",
      "issues": [],
      "risk_level": "LOW",
      "nested": {
        "a": {
          "b": {
            "c": "value"
          }
        }
      }
    }
    '''
    result = ClaudeParser.parse_response(deep_json)
    assert result is not None
    assert result["nested"]["a"]["b"]["c"] == "value"
