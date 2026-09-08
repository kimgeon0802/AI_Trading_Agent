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

# 2026-09-09 작업 종료
- Adapter Validation: COMPLETE
- Market Data Fallback: COMPLETE
- ECOS Macro Data: VERIFIED
- GPT Input Validation: PASS
- Claude API: NOT TESTED
- OpenAI API: NOT TESTED
- Next Step: Real GPT API Single-Stock Test
