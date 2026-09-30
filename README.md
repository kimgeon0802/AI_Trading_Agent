# AI Trading Agent

## 프로젝트 개요

이 프로젝트는 Multi-AI 기반 가상 투자 연구 시스템입니다.

단순 수익 창출이나 자동매매가 아닌, AI의 시장 해석 논리, 투자 결정 과정, 데이터 중요도, 예측 성공/실패 원인을 연구합니다.

주요 특징:
- **Multi-AI Trading Architecture**: Gemini, Claude를 활용한 Consensus 기반 판단
- **Safe Fallback**: API 장애 시 HOLD Fallback 처리
- **Prediction-to-Trade Traceability**: prediction_id를 통한 예측-거래-성과 추적
- **Comprehensive Reporting**: 상세 거래 보고서 및 AI 연구 보고서 자동 생성
- **Virtual Environment**: 가상 계좌 시스템 (실거래 불가)

---

# 현재 주요 파이프라인

```text
Market Data Collection
    ↓
Gemini 1차 분석 (방어적 JSON 파싱 적용)
    ↓
Tavily 뉴스 검색 및 동적 Query 생성
    ↓
STEP 2-1 관련성 필터 / score > 0.4 / URL & Title 중복 제거 / 최대 3개 선별
    ↓
STEP 2-2 Title + Summary + URL 포맷팅 (Summary ~450자 정제)
    ↓
Claude 2차 검증 (RAG + 뉴스 심층 분석)
    ↓
Consensus 최종 검증
    ↓
DB 저장 (predictions / agent_decisions)
    ↓
Research Report 자동 생성
```

---

# 현재 STEP 진행 상황

- **STEP 1 (MVP & 기본 파이프라인)**: 완료
- **STEP 2-1 (Tavily 뉴스 검색 및 관련성 필터링/중복 제거)**: 완료
- **STEP 2-2 (Tavily 뉴스 데이터 Claude 전달 구조 개선 - Title + Summary + URL)**: 완료
- **Gemini REAL JSON Parsing 안정화**: 완료 (Markdown 래퍼 방어적 처리)
- **개별 REAL API 및 단위/통합 테스트**: 전체 PASS

---

# 프로젝트 구조

```text
agents/          # Multi-AI Agent 로직 (Gemini, Claude, Multi-AI Orchestrator)
data/            # DB (trading.db), 보고서(reports/)
docs/            # 상세 문서
prompts/         # AI 프롬프트
runtime/         # 실행 및 관리(executor, tool_manager, search_provider 등)
tests/           # 테스트 (Block, Mock, Real)
```

---

# 테스트 및 검증 지침

- **Mock 테스트와 REAL API 검증 엄격 구분**: 유닛/통합 테스트 PASS가 곧바로 REAL E2E 성공을 의미하지 않으며, 실제 API 호출 및 로그 검증을 병행함.
- **최신 테스트 결과**: `test_step2_1_refinements.py`, `test_step2_2_claude_news.py`, `test_gemini_defensive_parsing.py` 등 STEP 2 관련 테스트 전면 성공.

---

# 다음 작업 (Next Task)

### STEP 2 REAL E2E Trace Verification
- 2026-09-30 REAL Trading Cycle에서 Tavily 검색 결과가 STEP 2-1 필터링과 STEP 2-2 Summary 정제를 거쳐 실제 Claude REAL API payload(`user_prompt`)까지 데이터 단위로 온전히 도달하는지 로그/트레이스를 직접 추적 및 검증.

---

# 중요 개발 규칙

- Python 내부에 투자 전략 로직을 넣지 않는다.
- 모든 투자 판단은 AI가 수행한다.
- 모든 AI 응답은 JSON 구조를 사용한다.
- 모든 사고 과정은 로그로 저장한다.
- 모든 거래 및 평가는 `prediction_id`를 기반으로 추적한다.
- 실제 증권 API 연동은 금지한다.
