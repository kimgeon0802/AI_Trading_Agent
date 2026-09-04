import logging

logger = logging.getLogger("RiskManager")

class RiskManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.max_position_size = 0.3  # Max 30% of total asset per ticker
        self.max_drawdown_limit = 0.1 # 10% MDD limit before defensive mode

    def get_risk_report(self, ticker, current_price, historical_prices=None, macro_data=None):
        portfolio = self.db.get_portfolio()
        holdings = self.db.get_holdings()
        
        total_asset = portfolio["total_asset"]
        
        # 1. Concentration Risk
        ticker_holding = next((h for h in holdings if h["ticker"] == ticker), None)
        current_position_value = (ticker_holding["quantity"] * current_price) if ticker_holding else 0
        concentration_ratio = current_position_value / total_asset if total_asset > 0 else 0
        
        # 2. Market Risk (Volatility)
        volatility = self._calculate_volatility(historical_prices) if historical_prices else 0.2
        
        # 3. Macro Risk (New)
        macro_risk_impact = 0.0
        if macro_data:
            # Example logic: Higher exchange rate (weak currency) and high interest rate increase risk
            exchange_rate = macro_data.get("exchange_rate", 1300)
            interest_rate = macro_data.get("interest_rate", 3.5)
            
            if exchange_rate > 1400: macro_risk_impact += 0.1
            if interest_rate > 4.0: macro_risk_impact += 0.1
        
        # 4. Risk Scoring
        risk_score = 0.2 # Base risk
        risk_score += (concentration_ratio * 0.4)
        risk_score += (volatility * 0.3)
        risk_score += macro_risk_impact
        
        risk_level = "Low"
        if risk_score > 0.6:
            risk_level = "High"
        elif risk_score > 0.35:
            risk_level = "Medium"
            
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "volatility": round(volatility, 2),
            "concentration_ratio": round(concentration_ratio, 2),
            "macro_risk_impact": round(macro_risk_impact, 2),
            "warnings": self._generate_warnings(concentration_ratio, total_asset, volatility, macro_risk_impact)
        }

    def _calculate_volatility(self, historical_prices):
        if not historical_prices or len(historical_prices) < 2:
            return 0.2
        
        # Simple volatility: standard deviation of daily returns
        returns = []
        for i in range(1, len(historical_prices)):
            returns.append((historical_prices[i] - historical_prices[i-1]) / historical_prices[i-1])
        
        import statistics
        return statistics.stdev(returns) * (252**0.5) # Annualized

    def _generate_warnings(self, concentration, total_asset, volatility, macro_risk_impact):
        warnings = []
        if concentration > self.max_position_size:
            warnings.append(f"Position concentration ({concentration*100:.1f}%) exceeds limit ({self.max_position_size*100:.1f}%)")
        if volatility > 0.4:
            warnings.append(f"High asset volatility detected ({volatility*100:.1f}% annualised).")
        if macro_risk_impact > 0.1:
            warnings.append("Macroeconomic conditions are adding to overall portfolio risk.")
        if total_asset < 5000000: # Low capital warning
            warnings.append("Portfolio value is low. Small trades may be inefficient.")
        return warnings
