import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from runtime.tool_manager.position_sizer import PositionSizer

logger = logging.getLogger("PortfolioManager")

class PortfolioManager:
    def __init__(self, db_manager, initial_cash: float = 0.0):
        self.db = db_manager
        self.sizer = PositionSizer()
        self.initial_cash = initial_cash

    def rebalance_portfolio(self, buy_candidates: List[Dict[str, Any]]):
        """
        Consensus 후 최종 후보들에 대해 리밸런싱 수행
        """
        portfolio = self.db.get_portfolio()
        holdings = self.db.get_holdings()

        target_amounts = self.sizer.calculate_target_positions(buy_candidates, portfolio, holdings)

        # 실제 매수/매도 로직 호출 (단계적으로 구현)
        logger.info(f"Rebalancing portfolio with target amounts: {target_amounts}")
        return target_amounts

    def ensure_initial_portfolio(self, initial_cash: Optional[float] = None):
        portfolio = self.db.get_portfolio()
        if not portfolio:
            cash = initial_cash if initial_cash is not None else self.initial_cash
            logger.info(f"Initializing portfolio with cash: {cash}")
            self.db.update_portfolio(cash, cash, datetime.now().isoformat())

    def get_current_state(self):
        portfolio = self.db.get_portfolio()
        holdings = self.db.get_holdings()
        return {
            "cash": portfolio["cash"],
            "total_asset": portfolio["total_asset"],
            "holdings": holdings
        }

    def execute_decision(self, ticker, decision_data, current_price, prediction_id=None):
        decision = decision_data["decision"]
        confidence = decision_data["confidence"]
        timestamp = datetime.now().isoformat()
        
        portfolio = self.db.get_portfolio()
        cash = portfolio["cash"]
        
        if decision == "BUY":
            self._handle_buy(ticker, cash, current_price, confidence, timestamp, prediction_id)
        elif decision == "SELL":
            self._handle_sell(ticker, current_price, confidence, timestamp, prediction_id)
        else:
            logger.info(f"HOLD decision for {ticker}. No action taken.")
        
        # Update total asset value
        self._update_total_asset(current_price, timestamp)

    def _handle_buy(self, ticker, available_cash, price, confidence, timestamp, prediction_id=None):
        # MVP logic: use 20% of cash for BUY (To be replaced by PositionSizer output)
        investment_amount = available_cash * 0.2
        quantity = int(investment_amount // price)
        
        if quantity > 0:
            total_cost = quantity * price
            new_cash = available_cash - total_cost
            
            # Update holding (average price calculation)
            holdings = self.db.get_holdings()
            current_holding = next((h for h in holdings if h["ticker"] == ticker), None)
            
            if current_holding:
                new_quantity = current_holding["quantity"] + quantity
                new_avg_price = ((current_holding["quantity"] * current_holding["average_price"]) + total_cost) / new_quantity
            else:
                new_quantity = quantity
                new_avg_price = price
            
            self.db.update_holding(ticker, new_quantity, new_avg_price)
            self.db.update_portfolio(new_cash, 0, timestamp) 
            self.db.save_trade(timestamp, ticker, "BUY", quantity, price, confidence, prediction_id=prediction_id)
            logger.info(f"BUY executed: {ticker}, {quantity} shares at {price}")
        else:
            logger.warning(f"Insufficient cash to BUY {ticker} at {price}")

    def _handle_sell(self, ticker, price, confidence, timestamp, prediction_id=None):
        holdings = self.db.get_holdings()
        current_holding = next((h for h in holdings if h["ticker"] == ticker), None)
        
        if current_holding and current_holding["quantity"] > 0:
            quantity = current_holding["quantity"]
            revenue = quantity * price
            
            portfolio = self.db.get_portfolio()
            new_cash = portfolio["cash"] + revenue
            
            self.db.update_holding(ticker, 0, 0)
            self.db.update_portfolio(new_cash, 0, timestamp)
            self.db.save_trade(timestamp, ticker, "SELL", quantity, price, confidence, prediction_id=prediction_id)
            logger.info(f"SELL executed: {ticker}, {quantity} shares at {price}")
        else:
            logger.warning(f"No holdings of {ticker} to SELL")

    def _update_total_asset(self, current_price, timestamp):
        portfolio = self.db.get_portfolio()
        holdings = self.db.get_holdings()
        
        holdings_value = sum(h["quantity"] * current_price for h in holdings)
        total_asset = portfolio["cash"] + holdings_value
        
        self.db.update_portfolio(portfolio["cash"], total_asset, timestamp)
        logger.info(f"Portfolio updated: Total Asset = {total_asset}")
