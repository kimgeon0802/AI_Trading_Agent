import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class TechnicalAnalysisEngine:
    """
    Historical market data based technical indicator calculator.
    Does not perform investment decisions.
    """
    
    def calculate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates indicators based on available price history.
        Assumes df contains 'close', 'high', 'low', 'volume' columns.
        """
        if df.empty or len(df) < 5: # Minimum data check
            return self._empty_result()
            
        results = {}
        
        # Returns
        results["returns"] = {
            "1d": float(df["change_rate"].iloc[-1]) if "change_rate" in df.columns else None,
            "5d": self._calculate_return(df, 5),
            "20d": self._calculate_return(df, 20),
            "60d": self._calculate_return(df, 60),
        }
        
        # Technical
        close = df["close"]
        results["technical"] = {
            "MA20": float(close.rolling(window=20).mean().iloc[-1]) if len(df) >= 20 else None,
            "MA60": float(close.rolling(window=60).mean().iloc[-1]) if len(df) >= 60 else None,
            "RSI": self._calculate_rsi(close, 14),
            "MACD": self._calculate_macd(close),
        }
        
        # Volume
        results["volume"] = {
            "current": float(df["volume"].iloc[-1]),
            "average_20d": float(df["volume"].rolling(window=20).mean().iloc[-1]) if len(df) >= 20 else None,
        }
        # relative volume calculation
        if results["volume"]["average_20d"] and results["volume"]["average_20d"] > 0:
            results["volume"]["relative"] = results["volume"]["current"] / results["volume"]["average_20d"]
        else:
            results["volume"]["relative"] = None
            
        return results

    def _calculate_return(self, df: pd.DataFrame, window: int) -> Optional[float]:
        if len(df) <= window:
            return None
        return float((df["close"].iloc[-1] - df["close"].iloc[-window]) / df["close"].iloc[-window] * 100)

    def _calculate_rsi(self, close: pd.Series, window: int) -> Optional[float]:
        if len(close) <= window:
            return None
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def _calculate_macd(self, close: pd.Series) -> Dict[str, Optional[float]]:
        if len(close) < 26:
            return {"MACD": None, "signal": None, "histogram": None}
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return {
            "MACD": float(macd.iloc[-1]),
            "signal": float(signal.iloc[-1]),
            "histogram": float(histogram.iloc[-1])
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "returns": {"1d": None, "5d": None, "20d": None, "60d": None},
            "technical": {"MA20": None, "MA60": None, "RSI": None, "MACD": None},
            "volume": {"current": None, "average_20d": None, "relative": None}
        }
