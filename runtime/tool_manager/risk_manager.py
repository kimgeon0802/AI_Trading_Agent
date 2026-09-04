import logging

logger = logging.getLogger("RiskManager")

class RiskManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.max_position_size = 0.3  # Max 30% of total asset per ticker
        self.max_drawdown_limit = 0.1 # 10% MDD limit before defensive mode

    def get_risk_report(self, ticker, current_price):
        portfolio = self.db.get_portfolio()
        holdings = self.db.get_holdings()
        
        total_asset = portfolio["total_asset"]
        cash = portfolio["cash"]
        
        # 1. Concentration Risk
        ticker_holding = next((h for h in holdings if h["ticker"] == ticker), None)
        current_position_value = (ticker_holding["quantity"] * current_price) if ticker_holding else 0
        concentration_ratio = current_position_value / total_asset if total_asset > 0 else 0
        
        # 2. Market Risk (Simulated for Phase 2)
        # In Phase 3+, this could use Beta, Volatility, etc.
        market_volatility = "Medium" # Placeholder
        
        # 3. Liquidity Risk
        # Since it's a simulator, we assume high liquidity.
        
        # 4. Drawdown Risk
        # Fetch from last evaluation or calculate
        # For now, a simple check
        
        risk_score = 0.3 # Base risk
        if concentration_ratio > self.max_position_size:
            risk_score += 0.4
        
        risk_level = "Low"
        if risk_score > 0.7:
            risk_level = "High"
        elif risk_score > 0.4:
            risk_level = "Medium"
            
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "concentration_ratio": round(concentration_ratio, 2),
            "warnings": self._generate_warnings(concentration_ratio, total_asset)
        }

    def _generate_warnings(self, concentration, total_asset):
        warnings = []
        if concentration > self.max_position_size:
            warnings.append(f"Position concentration ({concentration*100:.1f}%) exceeds limit ({self.max_position_size*100:.1f}%)")
        if total_asset < 5000000: # Low capital warning
            warnings.append("Portfolio value is low. Small trades may be inefficient.")
        return warnings
