import logging
from datetime import datetime
import os

logger = logging.getLogger("ResearchReportGenerator")

class ResearchReportGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        self.report_dir = "data/reports/research/"
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_path = os.path.join(self.report_dir, f"ai_research_report_{timestamp}.md")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# AI Research Report - {timestamp}\n\n")
            
            # 1. GPT Statistics
            f.write("## 1. GPT Analysis\n\n")
            gpt_stats = self.db.execute_query("""
                SELECT 
                    COUNT(*), 
                    SUM(CASE WHEN prediction = 'BUY' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN prediction = 'SELL' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN prediction = 'HOLD' THEN 1 ELSE 0 END),
                    AVG(confidence)
                FROM predictions
            """)
            s = gpt_stats[0]
            f.write(f"- Total Predictions: {s[0]}\n")
            f.write(f"- BUY: {s[1]}, SELL: {s[2]}, HOLD: {s[3]}\n")
            f.write(f"- Avg Confidence: {s[4]:.2f}\n\n")

            # 2. Claude Validation
            f.write("## 2. Claude Validation Effectiveness\n\n")
            claude_stats = self.db.execute_query("""
                SELECT 
                    SUM(CASE WHEN risk_assessment = 'PASS' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN risk_assessment = 'WARNING' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN risk_assessment = 'REJECT' THEN 1 ELSE 0 END)
                FROM agent_decisions WHERE model_name = 'claude'
            """)
            c = claude_stats[0]
            f.write(f"- PASS: {c[0]}, WARNING: {c[1]}, REJECT: {c[2]}\n\n")
            
            # 3. Performance Summary
            f.write("## 3. Performance Summary\n\n")
            perf = self.db.execute_query("""
                SELECT 
                    SUM(t.price * t.quantity) as total_val,
                    AVG(e.success)
                FROM trades t
                JOIN evaluation_logs e ON t.prediction_id = e.prediction_id
            """)
            f.write(f"- Total Executed Value: {perf[0][0]}\n")
            f.write(f"- Prediction Accuracy: {perf[0][1]*100:.2f}%\n")
            
        logger.info(f"Research report generated: {report_path}")
        return report_path
