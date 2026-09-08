import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("MarketDataAdapter")

class MarketDataAdapter:
    """
    Candidate DataFrame을 GPT Agent가 사용할 수 있는 
    JSON-compatible 데이터 구조로 변환하는 Adapter.
    """

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

    def validate_types(self, obj: Any, path: str = "root") -> List[str]:
        """
        데이터가 JSON-compatible Python 기본 타입인지 검증한다.
        허용: dict, list, str, int, float, bool, None
        """
        errors = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                errors.extend(self.validate_types(v, f"{path}.{k}"))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                errors.extend(self.validate_types(item, f"{path}[{i}]"))
        elif not isinstance(obj, (str, int, float, bool)) and obj is not None:
            errors.append(f"Invalid type at {path}: {type(obj).__name__}")
        return errors


    def convert_candidates(
        self,
        candidate_df: pd.DataFrame,
        portfolio_state: Dict[str, Any] = None,
        macro_data: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        DataFrame을 종목별 JSON-compatible List[Dict]로 변환한다.
        """
        if candidate_df.empty:
            return []

        market_data_list = []
        
        # DataFrame을 Dict 리스트로 변환
        candidates = candidate_df.to_dict(orient="records")

        for candidate in candidates:
            # 기본 데이터 변환
            clean_candidate = {
                k: self._convert_to_serializable(v)
                for k, v in candidate.items()
            }
            
            # GPT Agent에 맞는 표준화된 구조 구성
            # (기존 _collect_data와 호환성 유지)
            market_data = {
                "timestamp": datetime.now().isoformat(),
                "ticker": clean_candidate.get("ticker"),
                "name": clean_candidate.get("name"),
                "market": clean_candidate.get("market"),
                
                "market_data": {
                    "open": clean_candidate.get("open"),
                    "high": clean_candidate.get("high"),
                    "low": clean_candidate.get("low"),
                    "close": clean_candidate.get("close"),
                    "change_rate": clean_candidate.get("change_rate"),
                    "volume": clean_candidate.get("volume"),
                    "trading_value": clean_candidate.get("trading_value"),
                    "market_cap": clean_candidate.get("market_cap"),
                },
                
                "screening_data": {
                    k: v for k, v in clean_candidate.items()
                    if k not in ["ticker", "name", "market", "open", "high", "low", "close", "change_rate", "volume", "trading_value", "market_cap"]
                },
                
                "portfolio": portfolio_state or {},
                "macro_data": macro_data or {},
                # 추후 실제 AI 모드에서는 news/sentiment/risk를 별도 모듈에서 수집하여 추가 예정
                "news": [],
                "sentiment_analysis": {},
                "risk_report": {},
            }
            
            market_data_list.append(market_data)
            
        logger.info(f"Converted {len(market_data_list)} candidates for AI analysis.")
        return market_data_list
