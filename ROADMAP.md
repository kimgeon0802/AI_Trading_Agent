# 개발 로드맵

# Phase 1 — MVP [완료 - 2024-09-04]
(생략)

---

# Phase 2 — 분석 고도화 [완료 - 2026-09-04]
(생략)

---

# Phase 3 — 멀티 AI 구조 및 추적성 확보 [완료 - 2026-09-07]
(생략)

---

# Phase 4 — 연구 보고서 고도화 [진행 중]

목표:
- 실제 AI 판단 데이터를 기반으로 한 AI Research Report 자동 생성
- GPT vs Claude 성과 비교 분석 체계 구축
- 실제 데이터 기반 데이터 파이프라인 검증

진행할 내용:
1. AI Research Report 데이터 쿼리 및 분석 로직 구현.
2. 각 AI 판단 데이터와 실거래 ROI 상관관계 분석.
3. 시장 데이터 파이프라인 검증 [완료 - 2026-09-09]

---

# 2026-09-09 작업 기록

### 1-1. 시장 데이터 날짜 fallback 개선
- 2026-09-09 01시대 데이터 요청 시 pykrx의 데이터 0 반환 문제 해결.
- `market/market_data_collector.py`의 시장 데이터 수집 로직 수정.
- `get_trading_days` 대신 환경에 적합한 `stock.get_previous_business_days(year, month)` 사용.
- 최신 거래일 역순 탐색 구조로 실제 유효한 데이터 확보 후 사용.

### 1-2. 데이터 날짜 추적 구현
- `requested_date`, `actual_data_date`, `data_status`, `collected_at` 상태 정보 기록.
- FALLBACK_CONFIRMED 상태 처리 완료.

### 1-3. 실제 시장 데이터 수집 검증
- 2026-09-08 데이터 기준 KOSPI 943개, KOSDAQ 1,822개, 총 2,765개 정상 수집.

### 1-4. ScreeningEngine 검증
- 2,765개 데이터 → 후보 50개 선정 완료.
- `screening_score`의 정량적 선별 의도 준수.

### 1-5. CandidateValidator 검증
- 후보 50개 모두 통과.

### 1-6. MacroManager / ECOS 검증
- ECOS 실제 데이터 정상 연동 확인.
- exchange_rate, interest_rate, treasury_yield, cpi, gdp, unemployment_rate 정상 수집.

### 1-7. MarketDataAdapter 검증
- MarketPipeline → MarketDataAdapter → GPT Input Validation 단계 정상 동작 확인.

### 1-8. 실제 AI API 미호출 확인
- `VALIDATE_ADAPTER_ONLY=true` 설정으로 API 미호출 검증 완료.

### 1-9. 최종 검증 결과
- 실제 시장 데이터 수집 ~ GPT 입력 데이터 생성 전 구간 파이프라인 PASS.

---

# 검토 필요 사항
- `_is_data_valid()` 의 유효성 검증 로직은 최소한의 안전장치로 동작 중. 내일 코드 리뷰 시 실제 데이터 특성 고려하여 강화 필요 여부 검토.
- 거래일 탐색 로직의 정책 준수 여부(현재 날짜 우선, fallback 등) 재검토.

---

# Phase A — RAG Knowledge Base & Claude Integration [완료 - 2026-09-09]

## 완료 범위
- RAG Knowledge Base 설계 및 인벤토리 완료
- 7개 카테고리 Knowledge Base 구축 완료
    - Fundamental, Investors, Macro, Psychology, Risk, Strategy, Technical
- 총 31개 Markdown Knowledge 문서 확보
- Anti-Hallucination Rules 적용 및 검증 완료
- FAISS Vector Store 구축 완료
- 193개 chunks / 31개 source 정상 확인
- RAG Retrieval 정상 동작 확인 및 카테고리/Cross-category Retrieval 검증 완료
- Claude-only RAG architecture 적용 (GPTAgent는 RAG 영향 없이 기존 구조 유지)
- ClaudeAgent의 RAG Query 생성 및 Retrieval 연동 완료
- Retrieved Knowledge가 Claude Prompt Context에 주입되는 구조 확인 및 RAG failure graceful degradation 확인
- 실제 Claude + RAG E2E 동작 검증 및 GPT + Claude + Consensus 기존 파이프라인 regression 검증 완료

## 검증 완료 항목
- STEP 1~6, R1~R5 PASS
- Phase A A1~A3-6 전체 완료 및 최종 검증 PASS WITH WARNINGS
- Recovery 기록: 손상된 27개 Markdown 문서 복구 및 무결성 검증 완료

## Phase A 최종 의미
- `Markdown Knowledge Base → FAISS Vector Store → RAG Retrieval → ClaudeAgent → Claude Prompt Context Injection → Claude Analysis` 전체 파이프라인 연결 및 Claude의 RAG 활용 검증 완료.

**Phase A — COMPLETE**

---

---

# Phase B — GPT Web Search Integration [진행 예정]

목표: GPTAgent가 실시간 데이터(최신 뉴스, 공시 등)를 검색하고 분석에 활용할 수 있도록 Web Search Pipeline 구축 및 검증.

## 주요 설계 방향
- **Claude RAG와의 역할 분리:** Claude는 RAG를 통해 고도화된 도메인/장기 지식 활용, GPT는 Web Search를 통해 최신 외부 정보 활용.
- **GPTAgent 전용 Web Search:** GPTAgent에 검색 기능 통합, Claude RAG와는 독립적인 파이프라인 유지.
- **기존 구조 보호:** 기존 Decision JSON 계약, Consensus 로직, Market Pipeline 수정 금지.
- **비용/효율성 관리:** 검색 Query 최적화 및 단계적 검증(Mock → 1종목 → 다수 종목).
- **에러 처리:** 검색 실패 시 GPT가 기존 Market Data 기반으로 분석을 진행하는 Graceful Degradation 구현.

## 구현 단계
- STEP B1: GPT 구조(OpenAIClient, GPTAgent) 및 API 호환성 분석
- STEP B2: Web Search Client/Service 설계 및 Abstraction
- STEP B3: Candidate 기반 Query Builder 설계
- STEP B4: Search Result 정규화 및 GPT Prompt 주입 구현
- STEP B5: 에러 핸들링 및 실패 대응 구현
- STEP B6: GPT Decision 계약 무결성 검증 및 전체 파이프라인 regression 테스트

## 검증 기준
- Web Search 호출 성공 및 최신 정보 검색/parsing 정확도
- 기존 Decision 구조 유지 및 RAG/Claude 영향 없음
- 점진적 검증(1/3/5/10 stocks)을 통한 Multi-stock 안정성 확인
- API Rate limit 및 에러 상황 대응 테스트 완료

---
