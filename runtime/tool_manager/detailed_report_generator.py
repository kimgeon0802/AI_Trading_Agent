import logging
from datetime import datetime
import os

logger = logging.getLogger("DetailedReportGenerator")

class DetailedReportGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        self.report_dir = "data/reports/detailed/"
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_path = os.path.join(self.report_dir, f"detailed_trading_report_{timestamp}.md")
        
        portfolio = self.db.get_portfolio()
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Detailed Trading Report - {timestamp}\n\n")
            
            f.write("## 1. Portfolio Summary\n\n")
            if portfolio:
                f.write(f"- Current Portfolio Value: {portfolio['total_asset']}\n")
                f.write(f"- Available Cash: {portfolio['cash']}\n")
            else:
                f.write("Portfolio data not available.\n")
                
            f.write("\n## 2. Detailed Trade History\n\n")
            f.write("| Trade ID | Prediction ID | Timestamp | Ticker | Decision | Price | Quantity |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
            
            trades_data = self.db.execute_query("SELECT id, prediction_id, timestamp, ticker, decision, price, quantity FROM trades")
            for t in trades_data:
                f.write(f"| {t[0]} | {t[1]} | {t[2]} | {t[3]} | {t[4]} | {t[5]} | {t[6]} |\n")
            
        logger.info(f"Detailed report generated: {report_path}")
        return report_path
