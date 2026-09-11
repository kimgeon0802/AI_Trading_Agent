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
### Gemini
- [완료 / Real API 확인] Gemini 3.1 Flash-Lite 모델 변경 및 Batch API 통합.
- [완료 / Real API 확인] Gemini JSON Parser 강화 (설명문/Markdown fence 처리).

### Claude
- [완료 / Real API 확인] Claude API 응답 파서 강화 (Raw/Markdown/Explanation 포함 응답 처리).

### Real E2E
- [완료 / Real API 확인] AI 파이프라인 핵심 API 연결 및 응답 파싱 성공.
- `AI Pipeline Real E2E = SUCCESS` (단, Trading Cycle 내 보조 기능들은 검증 필요).

### Portfolio
- [완료 / 단위 테스트 확인] Portfolio 자산 평가 로직을 종목별 현재가 반영 구조로 개선.
- 기존 DB 데이터를 보존하며 정확한 Valuation 계산 로직으로 수정.

## Known Issues
### Portfolio Current Price Source [검증 필요]
- 개선된 Valuation 로직이 실제 KRX 최신가 데이터와 정확히 매칭되는지 확인 필요.
- MarketDataAdapter 데이터 흐름과 PortfolioManager의 가격 조회 경로 통합 검증.

### Report Generator [미해결 / 내일 작업]
- AI 파이프라인 단계별 성공/실패 여부를 반영하도록 보고서 생성 로직 개선 필요.
- 과거 데이터 집계 문제 해결 및 실행 세션별 결과 반영 필요.

### Runtime Cycle Status [미해결 / 내일 작업]
- Consensus FALLBACK 상황에서도 전체 사이클을 SUCCESS로 표시하는 문제 해결.
- 단계별(Gemini/Claude/Consensus/Portfolio) 상태 관리 및 전체 Cycle 상태 코드(SUCCESS/PARTIAL/FAILED) 도입.

## Next Session
### Step 1. Portfolio current price source 검증
- PortfolioManager가 사용하는 실시간 현재가 공급원(MarketDataAdapter vs Collector)의 정확성 확인.
- 종목별 가격 매칭 및 단위 검증.

### Step 2. Report Generator 수정
- trading cycle 데이터만 보고서에 반영되도록 로직 개선.

### Step 3. Runtime 성공/실패 상태 개선
- 각 파이프라인 단계별 성공/실패 마킹 및 전체 결과 마킹 로직 도입.

### Step 4. Full Real E2E 최종 검증
- 모든 수정 사항 적용 후 전체 Trading Cycle 최종 검증 (최소 호출).

## Development Rules
- **DB 보호**: `data/trading.db`를 임의로 삭제/초기화하지 않음. 데이터 분석 후 최소 수정.
- **Real API 보호**: 불필요한 Real API 호출 금지. 최종 검증에 필요한 최소 횟수만 사용.
- **결과 검증**: Mock PASS ≠ Real API PASS ≠ Real E2E PASS 엄격 구분.
- **원인 분석**: [확인]/[추정]/[예정] 구분 명시.
