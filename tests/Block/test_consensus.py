import pytest
from runtime.tool_manager.consensus_engine import ConsensusEngine

def test_consensus_agreement():
    gemini = {"decision": "BUY", "confidence": 0.8}
    claude = {"evaluation": "PASS", "score": 90}
    
    result = ConsensusEngine.analyze(gemini, claude)
    assert result["status"] == "AGREEMENT"
    assert result["decision"] == "BUY"

def test_consensus_conflict():
    gemini = {"decision": "BUY", "confidence": 0.8}
    claude = {"evaluation": "REJECT", "score": 20}
    
    result = ConsensusEngine.analyze(gemini, claude)
    assert result["status"] == "CONFLICT"
    assert result["decision"] == "HOLD"
    assert len(result["conflicts"]) > 0
