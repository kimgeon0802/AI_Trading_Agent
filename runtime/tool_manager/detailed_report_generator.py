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

    def get_portfolio_performance_metrics(self) -> Dict[str, Any]:
        """
        포트폴리오 성과 지표 (Daily Return, Cumulative Return, MDD) 계산
        - total_asset > 0 유효 스냅샷만 정제 (임시 스냅샷 제거)
        - 외부 입출금 (delta_cash == delta_total_asset & no trade) 감지 및 TWR 보정
        - snapshot 부족시 INSUFFICIENT_DATA 안전 반환
        """
        rows = self.db.execute_query(
            "SELECT cash, total_asset, timestamp FROM portfolio WHERE total_asset > 0 ORDER BY timestamp ASC, id ASC"
        )

        if not rows or len(rows) < 2:
            return {
                "daily_return": 0.0,
                "cumulative_return": 0.0,
                "mdd": 0.0,
                "status": "INSUFFICIENT_DATA"
            }

        # Fetch trades timestamps to detect trade existence
        trades_rows = self.db.execute_query("SELECT timestamp FROM trades ORDER BY timestamp ASC")
        trade_timestamps = set(t[0] for t in trades_rows if t and t[0])

        daily_eod_map = {}
        for cash, total_asset, ts in rows:
            if ts:
                date_str = ts.split("T")[0] if "T" in ts else ts.split(" ")[0]
                daily_eod_map[date_str] = (cash, total_asset, ts)

        daily_dates = sorted(daily_eod_map.keys())

        I_k = 1.0
        peak_I = 1.0
        max_drawdown = 0.0

        for i in range(1, len(rows)):
            prev_cash, prev_asset, prev_ts = rows[i-1]
            curr_cash, curr_asset, curr_ts = rows[i]

            if prev_asset <= 0:
                continue

            delta_cash = curr_cash - prev_cash
            delta_asset = curr_asset - prev_asset

            is_cash_flow = False
            if abs(delta_cash - delta_asset) < 1e-4 and abs(delta_cash) > 1e-4:
                if curr_ts not in trade_timestamps:
                    is_cash_flow = True

            if is_cash_flow:
                C_k = delta_asset
                if C_k > 0:
                    denom = prev_asset + C_k
                    r_k = (curr_asset - prev_asset - C_k) / denom if denom > 0 else 0.0
                else:
                    denom = prev_asset - abs(C_k)
                    r_k = (curr_asset - (prev_asset - abs(C_k))) / denom if denom > 0 else 0.0
            else:
                denom = prev_asset
                r_k = (curr_asset - prev_asset) / denom if denom > 0 else 0.0

            I_k = I_k * (1.0 + r_k)
            if I_k > peak_I:
                peak_I = I_k

            dd = (peak_I - I_k) / peak_I if peak_I > 0 else 0.0
            if dd > max_drawdown:
                max_drawdown = dd

        cumulative_return = (I_k - 1.0) * 100.0
        mdd = max_drawdown * 100.0

        daily_return = 0.0
        if len(daily_dates) >= 2:
            prev_d = daily_dates[-2]
            curr_d = daily_dates[-1]
            prev_c, prev_a, _ = daily_eod_map[prev_d]
            curr_c, curr_a, _ = daily_eod_map[curr_d]
            d_cash = curr_c - prev_c
            d_asset = curr_a - prev_a
            if abs(d_cash - d_asset) < 1e-4 and abs(d_cash) > 1e-4:
                C_k = d_asset
                denom = prev_a + C_k if C_k > 0 else prev_a - abs(C_k)
                daily_return = ((curr_a - prev_a - C_k) / denom * 100.0) if denom > 0 else 0.0
            else:
                daily_return = ((curr_a - prev_a) / prev_a * 100.0) if prev_a > 0 else 0.0
        elif len(rows) >= 2:
            prev_c, prev_a, prev_ts = rows[-2]
            curr_c, curr_a, curr_ts = rows[-1]
            d_cash = curr_c - prev_c
            d_asset = curr_a - prev_a
            if abs(d_cash - d_asset) < 1e-4 and abs(d_cash) > 1e-4:
                C_k = d_asset
                denom = prev_a + C_k if C_k > 0 else prev_a - abs(C_k)
                daily_return = ((curr_a - prev_a - C_k) / denom * 100.0) if denom > 0 else 0.0
            else:
                daily_return = ((curr_a - prev_a) / prev_a * 100.0) if prev_a > 0 else 0.0

        return {
            "daily_return": daily_return,
            "cumulative_return": cumulative_return,
            "mdd": mdd,
            "status": "SUCCESS"
        }

    def generate_report(self):
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.report_dir, f"detailed_report_{timestamp_str}.md")

        portfolio = self.db.get_portfolio()
        cash = portfolio["cash"] if portfolio else 0.0
        holdings = self.db.get_holdings()

        stock_value = 0.0
        for h in holdings:
            price = self.get_latest_price(h["ticker"])
            if price is not None:
                stock_value += h["quantity"] * price
            else:
                logger.error(f"Cannot generate report due to missing price for {h['ticker']}")
                raise ValueError(f"Price missing for {h['ticker']}")

        total_asset = cash + stock_value

        initial_row = self.db.execute_query("SELECT total_asset FROM portfolio ORDER BY id ASC LIMIT 1")
        initial_investment = initial_row[0][0] if initial_row else total_asset

        stats = self.get_trading_statistics()
        perf = self.get_portfolio_performance_metrics()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 상세 투자 보고서 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n")
            f.write("## 1. 포트폴리오 요약\n\n")
            f.write("| 항목 | 금액 |\n")
            f.write("| :--- | ---: |\n")
            f.write(f"| 초기 자본금 | {initial_investment:,.0f}원 |\n")
            f.write(f"| 현재 총 자산 | {total_asset:,.0f}원 |\n")
            f.write(f"| 보유 현금 | {cash:,.0f}원 |\n")
            f.write(f"| 주식 평가액 | {stock_value:,.0f}원 |\n")
            f.write(f"| 누적 손익 | {(total_asset - initial_investment):,.0f}원 |\n")
            f.write(f"| 누적 수익률 | {((total_asset - initial_investment) / initial_investment * 100) if initial_investment > 0 else 0.0:+.2f}% |\n\n")

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

            # 2.6 포트폴리오 성과 지표 (STEP 2-3)
            f.write("## 2.6 포트폴리오 성과 지표\n\n")
            f.write("| 항목 | 값 |\n")
            f.write("| :--- | ---: |\n")
            f.write(f"| Daily Return | {perf['daily_return']:+.2f}% |\n")
            f.write(f"| Cumulative Return | {perf['cumulative_return']:+.2f}% |\n")
            f.write(f"| Maximum Drawdown (MDD) | {perf['mdd']:.2f}% |\n")
            f.write(f"| 데이터 상태 | {perf['status']} |\n\n")

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
