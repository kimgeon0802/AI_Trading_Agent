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

## Current Status
- Gemini 3.1 Flash-Lite API 연동 성공 (HTTP 200).
- Claude API 파이프라인 연결 성공.
- Gemini 및 Claude 응답 파싱(JSON) 문제 해결 완료.
- AI 파이프라인 Real E2E 동작 확인 (Gemini → Claude → Consensus 성공).
- Portfolio 자산 평가(Valuation) 로직 개선 완료.

## Completed
### Claude Parser (오늘 완료)
- [완료 / 검증 완료] Markdown Code Fence, Nested JSON 구조 처리를 위한 JSON Parser 추출 로직 개선 (Commit: 06ddd16).
- [완료 / 검증 완료] 테스트 코드(`tests/Block/test_nested_json.py`)를 통해 중첩 JSON 응답 파싱 검증 완료.

### STEP 3 Trading Cycle Status Tracking (완료)
- [완료 / 검증 완료] `execute_single()` 내 fallback 상태 추적 및 prediction_ids, candidate summary 연결.
- [완료 / 검증 완료] Cycle Status (SUCCESS/PARTIAL/FAILED) 집계 및 Fallback HOLD 로직 구분 구현 (Commit: 197966c 등 참조).

### Portfolio & Reporting
- [완료 / 검증 완료] Portfolio performance metrics 추가 및 Prediction IDs 기반 cycle filtering 구현.

## Known Issues
### BLOCKER: KRX/pykrx 데이터 수집
- [진행 불가] KRX WAF 차단으로 인한 `pykrx` 데이터 수집 단계의 `JSONDecodeError` 발생.
- [대응] 실시간 파이프라인 통합 테스트 수행 불가. 데이터 수집 제한 해제 후 재시도 예정.

## Next Session
### Next 1. 데이터 수집 정상화 및 검증
- KRX 접근 제한 해제 확인 후 소량 종목 데이터 수집 테스트.
- 이후 전체시장 데이터 수집 1회 실행하여 ScreeningEngine 정상 동작 확인.

### Next 2. STEP 3 REAL 통합 테스트 재실행
- 데이터 수집 정상화 확인 후 파이프라인 전체 실행.
- 주요 확인 항목: Claude Parser 정상 동작 (`claude_result != None`), Cycle Status 및 Prediction ID 연계 확인.

### Next 3. Report Generator 연결 검증
- Cycle 성공 시 Prediction ID 기반 Trading Performance 필터링 정상 여부 확인.


## Development Rules
- **DB 보호**: `data/trading.db`를 임의로 삭제/초기화하지 않음. 데이터 분석 후 최소 수정.
- **Real API 보호**: 불필요한 Real API 호출 금지. 최종 검증에 필요한 최소 횟수만 사용.
- **결과 검증**: Mock PASS ≠ Real API PASS ≠ Real E2E PASS 엄격 구분.
- **원인 분석**: [확인]/[추정]/[예정] 구분 명시.
