import pytest
from runtime.tool_manager.query_builder import QueryBuilder, SearchCategory

def test_query_builder_valid_input():
    builder = QueryBuilder()
    data = {"name": "삼성전자", "ticker": "005930", "sector": "반도체"}
    macro = {"inflation": "2.0%"}
    
    queries = builder.build_queries(data, macro)
    
    assert len(queries) == 5
    assert any(q["category"] == SearchCategory.COMPANY_NEWS.value for q in queries)
    assert any(q["category"] == SearchCategory.SECTOR.value for q in queries)
    assert any(q["category"] == SearchCategory.MACRO.value for q in queries)

def test_query_builder_missing_data():
    builder = QueryBuilder()
    # name 없음
    data = {"ticker": "005930"}
    queries = builder.build_queries(data)
    assert len(queries) == 0

    # sector, macro 없음
    data = {"name": "삼성전자"}
    queries = builder.build_queries(data)
    assert len(queries) == 3 # News, Earnings, Risk
