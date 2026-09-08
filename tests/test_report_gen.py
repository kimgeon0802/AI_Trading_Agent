import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.research_report_generator import ResearchReportGenerator

def test_report_generation():
    test_db = "data/test_trading.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    db = DatabaseManager(db_path=test_db)
    
    # 1. Insert mock data to test full JOIN traceability
    # Prediction 1: Full flow
    p1 = db.save_prediction("AAPL", "BUY", 0.05, 80.0, "Reasoning 1", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.save_agent_decision(p1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'claude', 'PASS', 90.0, "Claude R1", 'PASS')
    db.save_agent_decision(p1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'consensus_manager', 'BUY', 0.0, "Consensus R1", None)
    db.save_trade(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "AAPL", "BUY", 10, 150.0, 80.0, p1)
    db.save_evaluation(p1, "Price: 155", "Success", True, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Prediction 2: Minimal flow (no trade, no evaluation)
    p2 = db.save_prediction("GOOG", "HOLD", 0.0, 50.0, "Reasoning 2", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 2. Generate Report
    generator = ResearchReportGenerator(db)
    report_path = generator.generate_report()
    
    # 3. Validate
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        print(content)
        assert "# AI 연구 보고서" in content
        assert "AAPL" in content
        assert "GOOG" in content
        assert "PASS" in content
        assert "미실행" in content # For GOOG
        
    print(f"Test passed! Report generated at: {report_path}")
    
    # Clean up
    os.remove(test_db)

if __name__ == "__main__":
    test_report_generation()
