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
- Claude API 파이프라인 연결 및 JSON Parser 로직 개선 완료.
- Detailed/Research Report Generator 연결 및 성능 지표 구현 완료.
- Trading Cycle / Report 연결 검증 완료 (Prediction IDs 필터링).
- 일 2회 Trading Cycle 실행을 위한 OS Scheduler(Windows Task Scheduler) 설계 완료.
- Trading Cycle의 오류 격리 및 복구 로직 검증 완료.

## Completed
### Reporting & Optimization
- [완료 / 검증 완료] DetailedReportGenerator 성능 지표(Daily/Cumulative Return, MDD) 및 거래 통계 구현.
- [완료 / 검증 완료] `price_map` 방식 도입을 통한 데이터 재수집 방지 및 효율화 (Commit: e984373).
- [완료 / 검증 완료] Gemini 명칭 레이블 일괄 변경 및 오해 소지 제거.

### Trading Cycle
- [완료 / 검증 완료] 시스템 오류 격리(Gemini/Tavily/Claude/Report 장애 처리) 및 포트폴리오 안전성 검증.
- [완료 / 검증 완료] 일 2회 완전한 Trading Cycle 실행 구조 및 데이터 독립성 확인.

## Known Issues
### BLOCKER: KRX/Naver 데이터 수집
- [진행 보류] KRX 로그인 및 시장 데이터 수집 접속 이슈.
- [대응] REAL 환경 통합 검증 중 접속 이슈 발생, 접속 정상화 이후 검증 재개 예정.

## Next Session (2026-09-17, 목요일)
### Next 1. REAL 통합 검증 재개
- KRX 접속 정상화 확인 후 1회 통합 사이클 실행.
- 주요 확인 사항: 데이터 재수집 발생 여부(`price_map` 검증), Claude/Gemini 최종 분석 흐름, Report Generator 최종 생성물.

### Next 2. Windows Task Scheduler 등록
- REAL 검증 완료 후 권장 설정(중복 실행 방지)에 따른 실운영 작업 등록.



## Development Rules
- **DB 보호**: `data/trading.db`를 임의로 삭제/초기화하지 않음. 데이터 분석 후 최소 수정.
- **Real API 보호**: 불필요한 Real API 호출 금지. 최종 검증에 필요한 최소 횟수만 사용.
- **결과 검증**: Mock PASS ≠ Real API PASS ≠ Real E2E PASS 엄격 구분.
- **원인 분석**: [확인]/[추정]/[예정] 구분 명시.
