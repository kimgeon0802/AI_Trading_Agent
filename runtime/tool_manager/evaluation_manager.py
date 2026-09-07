import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("EvaluationManager")

class EvaluationManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.reports_dir = "data/reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def run_evaluation(self, current_market_data):
        """
        Evaluate pending predictions based on current market data.
        current_market_data: { ticker: { price: float } }
        """
        logger.info("Starting evaluation of pending predictions...")
        pending = self.db.get_pending_evaluations()
        
        if not pending:
            logger.info("No pending predictions to evaluate.")
            return

        timestamp = datetime.now().isoformat()
        
        for pred in pending:
            ticker = pred["ticker"]
            if ticker in current_market_data:
                actual_price = current_market_data[ticker]["price"]
                # For Phase 1 Mock: We need the original price at prediction time.
                # In a real system, we'd fetch this from market_logs or trades.
                # Here, we'll look for the most recent trade price or market log for that ticker.
                
                # Simplified for MVP Evaluation:
                # We'll assume success if decision was BUY and price stayed same/up in mock,
                # or SELL and price down.
                
                prediction_decision = pred["prediction"]
                
                # Mock evaluation logic: 
                # Since we don't have historical "actual" price at prediction time saved easily,
                # we'll use a placeholder logic or fetch from trades.
                prediction_price = self._get_prediction_price(ticker, pred["timestamp"])
                
                if prediction_price:
                    return_pct = ((actual_price - prediction_price) / prediction_price) * 100
                    success = self._determine_success(prediction_decision, return_pct)
                    
                    evaluation_text = f"Price at prediction: {prediction_price}, Current: {actual_price}, Return: {return_pct:.2f}%"
                    
                    self.db.save_evaluation(
                        pred["id"],
                        f"{actual_price} ({return_pct:.2f}%)",
                        evaluation_text,
                        success,
                        timestamp
                    )
                    logger.info(f"Evaluated prediction {pred['id']} for {ticker}: {'SUCCESS' if success else 'FAIL'}")

        self.generate_reports()

    def _get_prediction_price(self, ticker, timestamp):
        # Try to get price from trades or market_logs
        query = "SELECT price FROM trades WHERE ticker = ? AND timestamp <= ? ORDER BY timestamp DESC LIMIT 1"
        result = self.db.execute_query(query, (ticker, timestamp))
        if result:
            return result[0][0]
        # Fallback to a default price if no trade found (for mock purposes)
        return 78000.0

    def _determine_success(self, decision, return_pct):
        if decision == "BUY":
            return return_pct > 0
        elif decision == "SELL":
            return return_pct < 0
        return True # HOLD is neutral

    def generate_reports(self):
        evaluations = self.db.get_evaluation_summaries()
        portfolio_history = self.db.execute_query("SELECT total_asset FROM portfolio ORDER BY timestamp ASC")
        
        # Calculate overall metrics
        total_return = 0.0
        max_drawdown = 0.0
        if portfolio_history:
            initial_asset = portfolio_history[0][0]
            current_asset = portfolio_history[-1][0]
            total_return = ((current_asset - initial_asset) / initial_asset) * 100
            
            # Max Drawdown calculation
            peak = 0
            for row in portfolio_history:
                asset = row[0]
                if asset > peak:
                    peak = asset
                dd = (peak - asset) / peak if peak > 0 else 0
                if dd > max_drawdown:
                    max_drawdown = dd
            max_drawdown *= 100

        # Daily Report
        today = datetime.now().strftime("%Y-%m-%d")
        daily_report_path = os.path.join(self.reports_dir, f"daily_evaluation_report_{today}.md")
        
        with open(daily_report_path, "w", encoding="utf-8") as f:
            f.write(f"# Daily Evaluation Report - {today}\n\n")
            
            f.write("## Performance Metrics\n")
            f.write(f"- **Total ROI:** {total_return:.2f}%\n")
            f.write(f"- **Max Drawdown:** {max_drawdown:.2f}%\n\n")
            
            f.write("## Trade Evaluations\n")
            f.write("| Timestamp | Ticker | Decision | Actual Result | Success |\n")
            f.write("|-----------|--------|----------|---------------|---------|\n")
            
            for ev in evaluations:
                # Only include today's evaluations
                if ev["timestamp"].startswith(today):
                    success_str = "✅ SUCCESS" if ev["success"] else "❌ FAIL"
                    f.write(f"| {ev['timestamp']} | {ev['ticker']} | {ev['prediction']} | {ev['result']} | {success_str} |\n")
            
            success_count = sum(1 for ev in evaluations if ev["success"] and ev["timestamp"].startswith(today))
            total_count = sum(1 for ev in evaluations if ev["timestamp"].startswith(today))
            
            if total_count > 0:
                accuracy = (success_count / total_count) * 100
                f.write(f"\n## Summary\n- Total Predictions: {total_count}\n- Success: {success_count}\n- Accuracy: {accuracy:.2f}%\n")

        logger.info(f"Generated daily report: {daily_report_path}")
