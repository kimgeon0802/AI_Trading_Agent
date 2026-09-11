import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from market.technical_analysis import TechnicalAnalysisEngine

logger = logging.getLogger("MarketDataAdapter")

class MarketDataAdapter:
    """
    Candidate DataFrame을 Gemini Agent가 사용할 수 있는 
    Gemini Analysis Dataset 구조로 변환하는 Adapter.
    """

    def __init__(self):
        self.tech_engine = TechnicalAnalysisEngine()

    def _convert_to_serializable(self, obj: Any) -> Any:
        """
        Numpy 타입, Timestamp 등을 Python 기본 타입으로 변환한다.
        """
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if pd.isna(obj):
            return None
        return obj

    def convert_candidates(
        self,
        candidate_df: pd.DataFrame,
        historical_data_map: Dict[str, pd.DataFrame] = None,
        portfolio_state: Dict[str, Any] = None,
        macro_data: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        DataFrame을 종목별 Gemini Analysis Dataset List[Dict]로 변환한다.
        """
        if candidate_df.empty:
            return []

        market_data_list = []
        candidates = candidate_df.to_dict(orient="records")

        for candidate in candidates:
            ticker = candidate.get("ticker")
            
            # Technical Analysis
            tech_results = self.tech_engine._empty_result()
            if historical_data_map and ticker in historical_data_map:
                tech_results = self.tech_engine.calculate(historical_data_map[ticker])
            
            # Gemini Analysis Dataset 구성
            market_data = {
                "ticker": ticker,
                "name": candidate.get("name"),
                "market": candidate.get("market"),
                
                "price_data": {
                    "current": self._convert_to_serializable(candidate.get("close")),
                    "previous_close": self._convert_to_serializable(candidate.get("close") - candidate.get("change", 0)),
                    "change_rate": self._convert_to_serializable(candidate.get("change_rate")),
                },
                "market_data": { # Legacy compatibility
                    "close": self._convert_to_serializable(candidate.get("close")),
                    "change_rate": self._convert_to_serializable(candidate.get("change_rate")),
                },
                
                "returns": tech_results["returns"],
                "technical": tech_results["technical"],
                "volume": tech_results["volume"],
                
                "market_context": {
                    "market_cap": self._convert_to_serializable(candidate.get("market_cap")),
                    "trading_value": self._convert_to_serializable(candidate.get("trading_value")),
                },
                
                "screening_context": {
                    "screening_score": self._convert_to_serializable(candidate.get("screening_score")),
                },
                
                "macro": macro_data or {},
                "portfolio": portfolio_state or {},
            }
            
            market_data_list.append(market_data)
            
        logger.info(f"Converted {len(market_data_list)} candidates for Gemini analysis.")
        return market_data_list
