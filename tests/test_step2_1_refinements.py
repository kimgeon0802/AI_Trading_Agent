import pytest
from agents.multi_ai.orchestrator import MultiAIOrchestrator
from runtime.tool_manager.web_search_client import SearchResult
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider

class MockDB:
    def save_agent_decision(self, *args, **kwargs):
        pass

def test_score_mapping_and_filter():
    orchestrator = MultiAIOrchestrator(db_manager=MockDB())
    
    # Create test search results with various scores, URLs, and titles
    res1 = SearchResult(query="test", title="Samsung Electronics stock surges", url="https://example.com/1", snippet="Samsung Electronics reported good earnings.", relevance=0.85)
    res1.score = 0.85

    res2 = SearchResult(query="test", title="Samsung Electronics stock surges", url="https://example.com/2", snippet="Duplicate title different URL.", relevance=0.90)
    res2.score = 0.90

    res3 = SearchResult(query="test", title="Other News", url="https://example.com/1", snippet="Duplicate URL different title.", relevance=0.80)
    res3.score = 0.80

    res4 = SearchResult(query="test", title="Low score irrelevant news", url="https://example.com/4", snippet="Unrelated content here.", relevance=0.2)
    res4.score = 0.2

    res5 = SearchResult(query="test", title="SK Hynix high score", url="https://example.com/5", snippet="SK Hynix news.", relevance=0.95)
    res5.score = 0.95

    search_results = [res1, res2, res3, res4, res5]
    gemini_analysis = {"analysis": {"point": "earnings"}}

    filtered = orchestrator._filter_news("005930", "Samsung Electronics", search_results, gemini_analysis)

    # 1. res4 should be filtered out (score 0.2 < 0.4 and not relevant to Samsung)
    # 2. res1 and res2 have identical title "Samsung Electronics stock surges" -> title deduplication keeps 1 (res2 has higher score 0.90)
    # 3. res1 and res3 have identical url "https://example.com/1" -> url deduplication keeps 1
    # 4. res5 has score 0.95 and mentions SK Hynix (not Samsung). Wait, does res5 mention Samsung? No. Is its score > 0.4? Yes (0.95 > 0.4). So res5 passes score filter.
    
    assert res4 not in filtered
    # Check max 3 results
    assert len(filtered) <= 3
    
    # Check that score mapping works properly
    for r in filtered:
        s = getattr(r, 'score', getattr(r, 'relevance', 0))
        assert s > 0.4 or "samsung" in (f"{r.title} {r.snippet}").lower()

def test_deduplication_exact():
    orchestrator = MultiAIOrchestrator(db_manager=MockDB())

    # Case: Duplicate URLs
    r1 = SearchResult(query="q", title="Title A", url="url1", snippet="Samsung Electronics 1", relevance=0.7)
    r1.score = 0.7
    r2 = SearchResult(query="q", title="Title B", url="url1", snippet="Samsung Electronics 2", relevance=0.8)
    r2.score = 0.8

    # Case: Duplicate Titles (different URLs)
    r3 = SearchResult(query="q", title="Title C", url="url3", snippet="Samsung Electronics 3", relevance=0.9)
    r3.score = 0.9
    r4 = SearchResult(query="q", title="Title C", url="url4", snippet="Samsung Electronics 4", relevance=0.6)
    r4.score = 0.6

    search_results = [r1, r2, r3, r4]
    gemini_analysis = {"analysis": {}}

    filtered = orchestrator._filter_news("005930", "Samsung Electronics", search_results, gemini_analysis)

    # r1 and r2 share url1 -> r2 kept (higher score or first encountered? url_deduped keeps first encounter: r1)
    # r3 and r4 share title "Title C" -> r3 kept (higher score or first: r3)
    urls = [r.url for r in filtered]
    titles = [r.title for r in filtered]

    assert len(urls) == len(set(urls))
    assert len(titles) == len(set(titles))
