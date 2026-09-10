from typing import List, Dict, Any
import logging

logger = logging.getLogger("PositionSizer")

class PositionSizer:
    MAX_POSITIONS = 10
    MAX_INVESTMENT_RATIO = 0.8 # 80%

    def calculate_target_positions(
        self, 
        buy_candidates: List[Dict[str, Any]], 
        portfolio: Dict[str, Any], 
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Risk Adjusted Equal Weight with Scaling 전략을 사용하여
        각 종목별 목표 투자 금액을 계산합니다.
        """
        cash = portfolio.get("cash", 0)
        investable_cash = cash * self.MAX_INVESTMENT_RATIO
        
        if not buy_candidates or investable_cash <= 0:
            return {}

        # 1. 후보군 제한 (MAX_POSITIONS)
        selected_candidates = buy_candidates[:self.MAX_POSITIONS]
        
        # 2. 기본 가중치 (Equal Weight)
        num_candidates = len(selected_candidates)
        base_weight = 1.0 / num_candidates
        
        target_positions = {}
        
        # 3. Scaling (Confidence + Risk - 단순화된 모델)
        # 실제 구현에서는 confidence와 risk 점수를 활용한 scaling 로직 추가
        total_scaled_weight = 0.0
        
        for cand in selected_candidates:
            ticker = cand["ticker"]
            confidence = cand.get("confidence", 0.5)
            
            # Confidence Scaling
            weight = base_weight * (confidence if confidence >= 0.8 else 0.5)
            
            target_positions[ticker] = weight
            total_scaled_weight += weight
            
        # 4. 정규화 (전체 합을 1.0으로, 이후 investable_cash 적용)
        if total_scaled_weight > 0:
            for ticker in target_positions:
                normalized_weight = target_positions[ticker] / total_scaled_weight
                target_positions[ticker] = normalized_weight * investable_cash
                
        return target_positions
