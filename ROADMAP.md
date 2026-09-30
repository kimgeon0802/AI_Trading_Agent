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

# Phase 4 — AI 파이프라인 고도화 및 안정화 [진행 중]

## Current Status (2026-09-30)
- Gemini 3.1 Flash-Lite API 연동 및 방어적 JSON 파싱(Markdown 래퍼 처리) 안정화 완료.
- Tavily 검색 쿼리 최적화 및 뉴스 관련성 필터링 / 중복 제거 (STEP 2-1) 완료.
- Claude 뉴스 전달 구조 개선 (`Title + Summary + URL`, STEP 2-2) 완료.
- 개별 REAL API 및 STEP 2 기능/단위/통합 테스트 검증 완료.

## Completed
### STEP 2-1 — Tavily 뉴스 검색 및 필터링 [완료]
- [완료 / 검증 완료] Gemini 1차 분석 결과 기반 동적 Tavily Query 생성 (`_build_search_query`: 종목명, 티커, 분석/이유 키워드 활용).
- [완료 / 검증 완료] Tavily REAL API 검색 (`max_results=10`, `search_depth="advanced"`).
- [완료 / 검증 완료] `SearchResult` 객체에 `score` 및 `relevance` 매핑 추가.
- [완료 / 검증 완료] 관련성 필터 (`score > 0.4` 또는 종목명/티커 포함), URL 중복 제거, Title 중복 제거, 최대 3개 뉴스 선별 (`_filter_news`).

### STEP 2-2 — Tavily 뉴스 → Claude 전달 구조 개선 [완료]
- [완료 / 검증 완료] 기존 `Title + URL` 전달 구조를 `Title + Summary + URL` 구조로 개선.
- [완료 / 검증 완료] Tavily `content`(`snippet`) 기반 Summary 정제 (`_format_summary()`, 최대 ~450자, 문장 경계 기준 자연스러운 종료).
- [완료 / 검증 완료] snippet 없음 및 검색 결과 없음 상황에 대한 안전한 Fallback 처리.
- [완료 / 검증 완료] 최대 3개 뉴스의 Summary 및 URL을 Claude(`ClaudeAgent.make_decision`) 프롬프트에 전달.

### Gemini REAL JSON Parsing 안정화 [완료]
- [완료 / 검증 완료] Gemini REAL API 응답에서 Markdown 래퍼(```json ... ```)가 포함될 경우 발생하는 `JSONDecodeError` 방어를 위한 방어적 파싱 로직 구현 (`GeminiAgent.execute_batch`).

### Reporting & Verification
- [완료 / 검증 완료] 상세/연구 보고서 생성기 및 Prediction Traceability 검증 완료.
- [완료 / 검증 완료] STEP 2 관련 단위 및 통합 테스트 (`test_step2_1_refinements.py`, `test_step2_2_claude_news.py`, `test_gemini_defensive_parsing.py`) 전체 PASS.

## Next Task
### STEP 2 REAL E2E Trace Verification
- **목표**: 2026-09-30 REAL Trading Cycle에서 동일한 Tavily 뉴스 데이터가 `Tavily REAL 결과` → `STEP 2-1 최종 선별` → `STEP 2-2 Summary` → `실제 Claude REAL API payload`까지 데이터 단위로 온전히 연결되었는지 로그/트레이스를 직접 추적 및 검증.
- **원칙**: 추정치나 Mock 성공을 REAL 성공으로 간주하지 않으며, 실제 로그 기반의 명확한 데이터 연속성 검증 수행.

## Known Issues
### BLOCKER: KRX/Naver 데이터 수집
- [진행 보류] KRX 로그인 및 시장 데이터 수집 접속 이슈.
- [대응] REAL 환경 통합 검증 중 접속 이슈 발생, 접속 정상화 이후 최종 통합 검증 재개 예정.

## Development Rules
- **DB 보호**: `data/trading.db`를 임의로 삭제/초기화하지 않음. 데이터 분석 후 최소 수정.
- **Real API 보호**: 불필요한 Real API 호출 금지. 최종 검증에 필요한 최소 횟수만 사용.
- **결과 검증**: Mock PASS ≠ Real API PASS ≠ Real E2E PASS 엄격 구분.
- **원인 분석**: [확인]/[추정]/[예정] 구분 명시.
