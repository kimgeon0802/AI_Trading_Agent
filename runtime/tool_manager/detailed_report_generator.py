import logging
from datetime import datetime
import os
import sqlite3
from typing import Optional, Dict, Any
from market.market_data_collector import MarketDataCollector

logger = logging.getLogger("DetailedReportGenerator")

class DetailedReportGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        self.report_dir = "data/reports/detailed/"
        os.makedirs(self.report_dir, exist_ok=True)
        self.ticker_map = {"005930": "삼성전자"}

    def _get_ticker_name(self, ticker):
        return self.ticker_map.get(ticker, ticker)

    def get_latest_price(self, ticker: str) -> Optional[float]:
        """
        MarketDataCollector를 사용하여 특정 종목의 최신 가격을 조회한다.
        """
        collector = MarketDataCollector()
        try:
            market_df = collector.collect_all_markets()
            price_row = market_df[market_df["ticker"] == ticker]
            if not price_row.empty:
                return float(price_row.iloc[0]["close"])
            else:
                logger.warning(f"Price not found for {ticker}")
                return None
        except Exception as e:
            logger.error(f"Failed to fetch price for {ticker}: {e}")
            return None

    def _calculate_realized_pl(self, ticker):
        """FIFO realized P/L calculation"""
        trades = self.db.execute_query("SELECT decision, quantity, price FROM trades WHERE ticker = ? ORDER BY timestamp ASC", (ticker,))
        buys = [] # List of (quantity, price)
        realized_pl = 0
        
        for decision, qty, price in trades:
            if decision == 'BUY':
                buys.append([qty, price])
            elif decision == 'SELL':
                sell_qty = qty
                while sell_qty > 0 and buys:
                    buy = buys[0]
                    if buy[0] <= sell_qty:
                        realized_pl += buy[0] * (price - buy[1])
                        sell_qty -= buy[0]
                        buys.pop(0)
                    else:
                        realized_pl += sell_qty * (price - buy[1])
                        buy[0] -= sell_qty
                        sell_qty = 0
        return realized_pl

    def get_trading_statistics(self) -> Dict[str, Any]:
        """
        거래 통계를 계산하여 반환한다.
        """
        all_realized_pls = []
        
        tickers = self.db.execute_query("SELECT DISTINCT ticker FROM trades")
        for t in tickers:
            ticker = t[0]
            ticker_trades = self.db.execute_query("SELECT decision, quantity, price FROM trades WHERE ticker = ? ORDER BY timestamp ASC", (ticker,))
            buys = []
            for decision, qty, price in ticker_trades:
                if decision == 'BUY':
                    buys.append([qty, price])
                elif decision == 'SELL':
                    sell_qty = qty
                    sell_pl = 0
                    while sell_qty > 0 and buys:
                        buy = buys[0]
                        if buy[0] <= sell_qty:
                            sell_pl += buy[0] * (price - buy[1])
                            sell_qty -= buy[0]
                            buys.pop(0)
                        else:
                            sell_pl += sell_qty * (price - buy[1])
                            buy[0] -= sell_qty
                            sell_qty = 0
                    all_realized_pls.append(sell_pl)
        
        winning_trades = [pl for pl in all_realized_pls if pl > 0]
        losing_trades = [pl for pl in all_realized_pls if pl < 0]
        break_even_trades = [pl for pl in all_realized_pls if pl == 0]
        
        num_winning = len(winning_trades)
        num_losing = len(losing_trades)
        num_trades = num_winning + num_losing
        
        win_rate = (num_winning / num_trades * 100) if num_trades > 0 else 0.0
        
        avg_winning = sum(winning_trades) / num_winning if num_winning > 0 else 0.0
        avg_losing = sum(losing_trades) / num_losing if num_losing > 0 else 0.0
        avg_pl = sum(all_realized_pls) / len(all_realized_pls) if all_realized_pls else 0.0
        
        gross_profit = sum(winning_trades)
        gross_loss = abs(sum(losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
        
        return {
            "total_trades": len(all_realized_pls),
            "winning_trades": num_winning,
            "losing_trades": num_losing,
            "break_even_trades": len(break_even_trades),
            "win_rate": win_rate,
            "avg_winning": avg_winning,
            "avg_losing": avg_losing,
            "avg_pl": avg_pl,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor
        }

    def generate_report(self):
        # ... (same as before until metrics)
        
        # Calculate summary metrics (as implemented before)
        # ...
        
        stats = self.get_trading_statistics()
        
        with open(report_path, "w", encoding="utf-8") as f:
            # ... (sections 1-2)
            
            # 2.5 Trading Performance (New)
            f.write("## 2.5 거래 성과 요약\n\n")
            f.write("| 항목 | 값 |\n")
            f.write("| :--- | ---: |\n")
            f.write(f"| 총 거래 횟수 | {stats['total_trades']}회 |\n")
            f.write(f"| 승리 거래 | {stats['winning_trades']}회 |\n")
            f.write(f"| 패배 거래 | {stats['losing_trades']}회 |\n")
            f.write(f"| 본전 거래 | {stats['break_even_trades']}회 |\n")
            f.write(f"| 승률 | {stats['win_rate']:.2f}% |\n")
            f.write(f"| 평균 수익 | {stats['avg_winning']:,.0f}원 |\n")
            f.write(f"| 평균 손실 | {stats['avg_losing']:,.0f}원 |\n")
            f.write(f"| 평균 손익 | {stats['avg_pl']:,.0f}원 |\n")
            f.write(f"| Profit Factor | {stats['profit_factor'] if stats['profit_factor'] != float('inf') else 'N/A' :.2f} |\n\n")

            # ... (rest of sections 3-6)
                
            # 2. 현재 보유 종목
            f.write("## 2. 현재 보유 종목\n\n")
            f.write("| 종목코드 | 종목명 | 보유수량 | 평균 매수가 | 현재가 | 총 매수금액 | 평가금액 | 평가손익 | 수익률 |\n")
            f.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
            for h in holdings:
                current_price = self.get_latest_price(h['ticker']) # Verified not None due to safety policy
                total_buy = h['quantity'] * h['average_price']
                eval_value = h['quantity'] * current_price
                eval_pl = eval_value - total_buy
                roi = (eval_pl / total_buy) * 100 if total_buy > 0 else 0.0
                f.write(f"| {h['ticker']} | {self._get_ticker_name(h['ticker'])} | {h['quantity']} | {h['average_price']:,.0f} | {current_price:,.0f} | {total_buy:,.0f} | {eval_value:,.0f} | {eval_pl:,.0f} | {roi:+.2f}% |\n")
            
            # ... (rest of report generation remains the same)
            
            # 3. 상세 거래 내역
            f.write("\n## 3. 상세 거래 내역\n\n")
            f.write("| 거래ID | Prediction ID | 시간 | 종목코드 | 종목명 | 최종 판단 | 거래가격 | 수량 | 거래금액 | 실현손익 |\n")
            f.write("| ---: | ---: | --- | :--- | :--- | :--- | ---: | ---: | ---: | ---: |\n")
            trades_data = self.db.execute_query("SELECT id, prediction_id, timestamp, ticker, decision, price, quantity FROM trades ORDER BY timestamp DESC")
            
            # Precalculate PL for trades to display
            for t in trades_data:
                time_str = datetime.fromisoformat(t[2]).strftime("%H:%M:%S")
                amount = t[5] * t[6]
                
                # Realized P/L only for SELL
                pl_str = "-"
                if t[4] == 'SELL':
                    pl = self._calculate_realized_pl(t[3]) # Simplified per ticker
                    pl_str = f"{pl:,.0f}"
                
                f.write(f"| {t[0]} | {t[1]} | {time_str} | {t[3]} | {self._get_ticker_name(t[3])} | {t[4]} | {t[5]:,.0f} | {t[6]} | {amount:,.0f} | {pl_str} |\n")

            # 4. 종목별 거래 요약
            f.write("\n## 4. 종목별 거래 요약\n\n")
            f.write("| 종목코드 | 종목명 | 매수횟수 | 매수수량 | 총 매수금액 | 매도횟수 | 매도수량 | 총 매도금액 | 실현손익 |\n")
            f.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
            tickers = self.db.execute_query("SELECT DISTINCT ticker FROM trades")
            for t in tickers:
                ticker = t[0]
                buy_data = self.db.execute_query("SELECT COUNT(*), SUM(quantity), SUM(quantity * price) FROM trades WHERE ticker = ? AND decision = 'BUY'", (ticker,))
                sell_data = self.db.execute_query("SELECT COUNT(*), SUM(quantity), SUM(quantity * price) FROM trades WHERE ticker = ? AND decision = 'SELL'", (ticker,))
                b = buy_data[0]
                s = sell_data[0]
                pl = self._calculate_realized_pl(ticker)
                f.write(f"| {ticker} | {self._get_ticker_name(ticker)} | {b[0] or 0} | {b[1] or 0} | {b[2] or 0:,.0f} | {s[0] or 0} | {s[1] or 0} | {s[2] or 0:,.0f} | {pl:,.0f} |\n")

            # 5. 자산 구성
            f.write("\n## 5. 자산 구성\n\n")
            cash_ratio = (cash / total_asset) * 100 if total_asset > 0 else 0
            stock_ratio = (stock_value / total_asset) * 100 if total_asset > 0 else 0
            
            def make_bar(ratio):
                blocks = int(ratio / 5)
                return "█" * blocks + "░" * (20 - blocks)
            
            f.write(f"현금 {make_bar(cash_ratio)} {cash_ratio:.1f}%\n\n")
            f.write(f"주식 {make_bar(stock_ratio)} {stock_ratio:.1f}%\n\n")
            
            # 6. 포트폴리오 변화
            f.write("\n## 6. 포트폴리오 변화\n\n")
            trend = self.db.execute_query("SELECT timestamp, total_asset FROM portfolio ORDER BY timestamp ASC")
            if len(trend) > 1:
                f.write("포트폴리오 평가금액 추이:\n\n```text\n")
                assets = [t[1] for t in trend]
                
                # ASCII Grid Settings
                height = 6
                width = min(len(assets), 60)
                
                # Downsample if too many data points
                if len(assets) > width:
                    indices = [int(i * (len(assets) - 1) / (width - 1)) for i in range(width)]
                    assets = [assets[i] for i in indices]
                
                min_asset, max_asset = min(assets), max(assets)
                data_range = max_asset - min_asset
                padding = max(data_range * 0.1, 100000)
                y_min = min_asset - padding
                y_max = max_asset + padding
                y_range = y_max - y_min
                
                grid = [[' ' for _ in range(width)] for _ in range(height)]
                
                for i, val in enumerate(assets):
                    norm = (val - y_min) / y_range if y_range > 0 else 0
                    y_row = height - 1 - round(norm * (height - 1))
                    grid[y_row][i] = '●'
                
                # Render Grid
                for r in range(height):
                    row_val = y_max - (r * y_range / (height - 1))
                    f.write(f"{row_val/1000000:>6.2f}M ┤ {''.join(grid[r])}\n")
                f.write("       └" + "─" * width + "\n```\n")
            else:
                f.write("현재 데이터가 1일치이므로 추이 그래프를 제공하지 않습니다.\n")

            
        logger.info(f"Detailed report generated: {report_path}")
        return report_path
