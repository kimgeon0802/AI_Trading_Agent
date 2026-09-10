from enum import Enum
from typing import List, Dict, Any, Optional

class SearchCategory(Enum):
    COMPANY_NEWS = "company_news"
    EARNINGS = "earnings"
    COMPANY_RISK = "company_risk"
    SECTOR = "sector"
    MACRO = "macro"

class QueryBuilder:
    def build_queries(self, candidate_data: Dict[str, Any], macro_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """
        종목과 매크로 데이터를 기반으로 검색 쿼리 목록을 생성합니다.
        """
        queries = []
        name = candidate_data.get("name")
        ticker = candidate_data.get("ticker")
        sector = candidate_data.get("sector")

        if not name:
            return []

        # 1. 최신 기업 뉴스
        queries.append({
            "category": SearchCategory.COMPANY_NEWS.value,
            "query": f"{name} 최신 뉴스"
        })

        # 2. 실적 / 공시
        queries.append({
            "category": SearchCategory.EARNINGS.value,
            "query": f"{name} 최근 실적 공시"
        })

        # 3. 기업 이슈 / 리스크
        queries.append({
            "category": SearchCategory.COMPANY_RISK.value,
            "query": f"{name} 최근 기업 이슈 리스크"
        })

        # 4. 산업 / 섹터 이슈 (데이터 존재 시에만)
        if sector:
            queries.append({
                "category": SearchCategory.SECTOR.value,
                "query": f"{name} {sector} 산업 전망"
            })

        # 5. 거시경제 / 정책 (데이터 존재 시에만)
        if macro_data:
            queries.append({
                "category": SearchCategory.MACRO.value,
                "query": "한국 금리 환율 최근 경제 정책"
            })

        return queries
