import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger("RefinementEngine")

class RefinementEngine:
    def __init__(self, target_min=10, target_max=15):
        self.target_min = target_min
        self.target_max = target_max
    
    def refine(self, candidates: pd.DataFrame) -> pd.DataFrame:
        """
        Screening 결과(50개)를 기반으로 핵심 후보 종목(10~15개)으로 압축.
        """
        if candidates.empty:
            return candidates

        # 1. 후보군 수가 target_min 이하면 그대로 반환
        if len(candidates) <= self.target_min:
            return candidates

        # 2. Screening Score 기준 정렬 (최상위부터)
        df = candidates.sort_values(by="screening_score", ascending=False).copy()

        # 3. Diversification/Concentration Check (Optional)
        # Sector 데이터가 있는 경우만 동작, 없으면 Graceful degradation
        if "sector" in df.columns:
            # 예: 같은 섹터가 과도하게 많으면 (예: 5개 초과) 제한하는 로직 구현 가능
            # 현재는 기본 정렬 유지하며 인터페이스만 확보
            pass
        
        # 4. 후보 수 압축 (Target Max 범위 내에서 최상위 후보 선정)
        # 단순히 Top N을 선택하되, 10~15개 사이에서 조정
        num_to_select = min(len(df), self.target_max)
        refined_df = df.head(num_to_select).copy()
        
        logger.info(f"Refinement: {len(candidates)} -> {len(refined_df)} candidates")
        
        return refined_df
