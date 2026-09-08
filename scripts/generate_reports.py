import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.research_report_generator import ResearchReportGenerator
from runtime.tool_manager.detailed_report_generator import DetailedReportGenerator

def generate_final_reports():
    db_path = "data/test_trading.db"
    if not os.path.exists(db_path):
        print("Test DB not found. Run generate_mock_data.py first.")
        return

    db = DatabaseManager(db_path=db_path)
    
    # 1. Research Report
    research_gen = ResearchReportGenerator(db)
    research_path = research_gen.generate_report()
    print(f"Research Report generated at: {research_path}")
    
    # 2. Detailed Report
    detailed_gen = DetailedReportGenerator(db)
    detailed_path = detailed_gen.generate_report()
    print(f"Detailed Report generated at: {detailed_path}")

if __name__ == "__main__":
    generate_final_reports()
