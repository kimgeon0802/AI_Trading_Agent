import random
import logging

logger = logging.getLogger("MarketSimulator")

class MarketSimulator:
    def __init__(self):
        self.prices = {
            "005930": 78500.0,  # 삼성전자
            "000660": 190000.0, # SK하이닉스
            "035420": 185000.0  # NAVER
        }
        self.market_conditions = ["bullish", "bearish", "sideways"]
        self.current_condition = "sideways"

    def set_condition(self, condition):
        if condition in self.market_conditions:
            self.current_condition = condition
            logger.info(f"Market condition set to: {condition}")

    def simulate_step(self):
        """Simulate one step of price movements for all tickers."""
        for ticker in self.prices:
            # Base volatility
            change_pct = random.uniform(-3, 3)
            
            # Occasional big moves (5% chance)
            if random.random() < 0.05:
                change_pct = random.uniform(-10, 10)
            
            # Adjust based on market condition
            if self.current_condition == "bullish":
                change_pct += random.uniform(0, 2)
            elif self.current_condition == "bearish":
                change_pct -= random.uniform(0, 2)
                
            old_price = self.prices[ticker]
            new_price = old_price * (1 + change_pct / 100)
            self.prices[ticker] = round(new_price, -2) # Round to nearest 100
            
            logger.debug(f"Simulated price for {ticker}: {old_price} -> {self.prices[ticker]} ({change_pct:.2f}%)")

    def get_price(self, ticker):
        return self.prices.get(ticker, 10000.0)

    def get_all_prices(self):
        return {ticker: {"price": price} for ticker, price in self.prices.items()}
