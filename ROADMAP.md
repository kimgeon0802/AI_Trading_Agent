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

# 2026-09-10 작업 기록

## 1. 오늘 작업 내용

### 1-1. Gemini 1차 분석 구조 정리
- Gemini 3.6 Flash를 1차 분석 모델로 사용하도록 구조를 정리했습니다.
- Google Search Grounding은 제거했습니다.
- 현재 Gemini 역할:
  - 1차 투자 분석 수행
  - Refinement 후보 중 최대 10개 후보 선정
- Gemini 비대상 역할:
  - 투자금 배분 ❌, Position Sizing ❌, 실제 매매 ❌ (해당 역할들은 담당하지 않음)
- 실제 최신 웹 정보 검색은 Tavily가 담당합니다.

### 1-2. Tavily SearchProvider 구현
- 신규 파일 생성:
  - `runtime/tool_manager/search_provider.py`
  - `runtime/tool_manager/tavily_search_provider.py`
- 구조:
  ```text
  SearchProvider (Abstract)
          │
          └── TavilySearchProvider
                  │
                  ↓
               Tavily API
                  │
                  ↓
            SearchResult
  ```
- 기존 `SearchResult` contract를 재사용하여 검색 결과의 표준화를 일관되게 유지했습니다.
- Tavily SDK (`tavily-python`)를 디펜던시에 추가했습니다.

### 1-3. Tavily Error Handling 구현
- 기존 `classify_error`를 활용하여 Tavily API 오류를 체계적으로 분류하고 로깅하도록 구현했습니다.
- 고려된 오류 상황: API Key 오류, 429 Rate Limit, Timeout, Network Error, Empty Result, API Response Error.
- API Key는 코드 내 하드코딩하지 않고 환경변수 `TAVILY_API_KEY`를 사용하도록 설계했습니다.

### 1-4. Gemini → Tavily → Claude Mock 통합
- 다음 파이프라인을 Mock 환경에서 성공적으로 연결했습니다:
  ```text
  Screening
      ↓
  Refinement
      ↓
  MarketDataAdapter
      ↓
  Gemini
      ↓
  selected_candidates
      ↓
  Tavily SearchProvider
      ↓
  SearchResult
      ↓
  Claude
      ↓
  Consensus
  ```
- 핵심 역할 분리:
  - **Gemini**: 1차 분석 + 최대 10개 후보 선정
  - **Tavily**: 최신 웹 정보 검색
  - **Claude**: Gemini 결과 + Tavily 결과 + RAG 기반 2차 심층 분석
  - **Consensus**: 최종 판단 및 합의
  - **PositionSizer**: 투자 비중 / 투자금 / 수량 결정
  - **PortfolioManager**: 가상 매매 실행

### 1-5. Gemini Mock 결과 확장
- Gemini Mock 결과에 `selected_candidates` 필드를 추가하여 후속 Tavily 검색 대상과 자연스럽게 연결했습니다.
- Gemini가 선정한 후보는 최대 10개로 제한하는 구조를 채택했습니다.
- 중요한 후보 흐름:
  ```text
  Screening 50
      ↓
  Refinement 10~15
      ↓
  Gemini
      ↓
  최대 10개 선정
      ↓
  Tavily 검색
  ```
  전체 KOSPI/KOSDAQ 종목에 대해 불필요하게 검색하지 않는 고효율 구조입니다.

### 1-6. Claude 연동
- `agents/claude_agent/agent.py`의 `make_decision` 메서드에 Tavily 검색 결과를 전달할 수 있도록 보완했습니다.
- Claude가 `Gemini 1차 분석 + Tavily 최신 검색 결과 + 기존 RAG` 세 가지 차원의 정보를 모두 활용하여 심층 결정을 도출할 수 있는 구조입니다.
- Claude RAG와 Consensus 구조는 기존 contract를 안정적으로 유지했습니다.

---

## 2. 오늘 테스트 결과

### Gemini
- Block 테스트: **PASS**
- Mock 테스트: **PASS**
- *주석: Gemini 실제 API는 현재 quota 문제로 추가 실행하지 않았으며, Google Search Grounding은 성공적으로 제거된 상태입니다.*

### Tavily
- Block 테스트: **PASS**
- Mock 테스트: **PASS**
- Real 단일 종목 테스트: **PASS**
  - 테스트 대상 종목: `000660 / SK하이닉스`
  - 검색 Query: `SK하이닉스 최신 뉴스`
  - 실제 Tavily API 호출 횟수: **1회**
  - 검색 결과 개수: **5개**
  - `SearchResult` contract 변환: **PASS**
  - 검증된 주요 필드: `title`, `url`, `content`, `published_date`, `score`

---

## 3. API 호출량 기록
- **Gemini API**: 0회
- **Tavily API**: 1회
- **Claude API**: 0회
- **OpenAI API**: 0회
- *Mock 테스트 내 모든 외부 API 호출 횟수는 **0회**임을 기록합니다.*

---

## 4. 현재 프로젝트 상태

### 파이프라인 구조
```text
Screening
    ↓
Refinement
    ↓
MarketDataAdapter
    ↓
Gemini
    │
    └── selected_candidates (최대 10)
             ↓
       SearchProvider
             ↓
       TavilySearchProvider
             ↓
        SearchResult
             ↓
           Claude
             ↓
         Consensus
             ↓
       PositionSizer
             ↓
      PortfolioManager
```

### 상세 상태 요약
- **Gemini 1차 분석**: 구현 완료 / Mock 검증 완료 / Real API 검증 대기
- **Tavily SearchProvider**: 구현 완료 / Block 검증 완료 / Mock 검증 완료 / Real 단일 검색 검증 완료
- **Gemini → Tavily → Claude**: Mock 통합 검증 완료
- **전체 Real E2E**: 아직 수행하지 않음

---

## 5. 내일 작업 기록 (다음 단계 계획)

### 1차 목표
- **Gemini → Tavily → Claude 실제 파이프라인 연동 검증**

### 실행 예정 순서
1. Gemini Real API 상태 확인 및 활성화 여부 점검
2. Gemini 1차 분석 결과의 정확성 확인
3. Gemini 결과에서 도출된 `selected_candidates` 유효성 확인
4. 선정된 후보(최대 10개)에 대해서만 Tavily 검색 수행
5. Tavily 검색 결과 내용 및 표준화 변환 상태 확인
6. Gemini 1차 분석 결과 및 Tavily 최신 검색 결과를 Claude에 안정적으로 전달
7. Claude 2차 심층 RAG 분석 결과 확인
8. Consensus 모듈과의 정상 연결 및 합의 도출 프로세스 확인
9. 필요한 경우 단일 종목 Real E2E 검증 우선 수행
10. 이후 Multi-stock Real 테스트 단계적 검토

### API 테스트 관리 원칙
- Real API 테스트는 **반드시 호출 횟수를 엄격히 제한**하며, 실패 시 무한 루프나 과다 청구를 방지하기 위해 **자동 retry를 수행하지 않습니다.**
- OpenAI API는 현재 아키텍처에서 사용하지 않는 구조이며, 향후 이번 파이프라인 검증 과정에서도 **호출하지 않는 원칙**을 유지합니다.

---

## 6. 다음 단계의 목표 아키텍처

```text
Screening 50
 ↓
Refinement 10~15
 ↓
Adapter
 ↓
Gemini 1차 분석
 ↓
최대 10개 후보
 ↓
Tavily 최신 정보 검색
 ↓
Claude 2차 심층 분석 + RAG
 ↓
Consensus
 ↓
PositionSizer
 ↓
PortfolioManager
```

- **핵심 아키텍처 원칙**: Gemini가 투자금을 직접 배분하거나 `PositionSizer` 역할을 가로채지 않고, 철저히 1차 후보 선별 및 기본 분석 전문가로서 동작하도록 역할을 선명하게 분리·유지합니다.

