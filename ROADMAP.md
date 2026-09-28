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

## Current Status (2026-09-28)
- Gemini 3.1 Flash-Lite API 연동 성공 (HTTP 200).
- Claude API 파이프라인 연결 및 JSON Parser 로직 개선 완료.
- Detailed/Research Report Generator 연결 및 성능 지표 구현 완료.
- Trading Cycle / Report 연결 검증 완료 (Prediction IDs 필터링).
- E2E 테스트 및 최종 검증 스크립트(`test_final_verification.py`, `run_real_e2e_diagnostic.py`) 구축 완료.
- 일 2회 Trading Cycle 실행 구조 정립.

## Completed
### Reporting & Optimization
- [완료 / 검증 완료] DetailedReportGenerator 성능 지표(Daily/Cumulative Return, MDD) 및 거래 통계 구현.
- [완료 / 검증 완료] `price_map` 방식 도입을 통한 데이터 재수집 방지 및 효율화.
- [완료 / 검증 완료] Gemini 명칭 레이블 일괄 변경.

### Trading Cycle & Verification
- [완료 / 검증 완료] 시스템 오류 격리 및 포트폴리오 안전성 검증.
- [완료 / 검증 완료] 최종 E2E 통합 검증 스크립트 구현 및 테스트.

## Known Issues
### BLOCKER: KRX/Naver 데이터 수집
- [진행 보류] KRX 로그인 및 시장 데이터 수집 접속 이슈.
- [대응] REAL 환경 통합 검증 중 접속 이슈 발생, 접속 정상화 이후 최종 통합 검증 재개 예정.

## Future Milestones
### 1. KRX 연동 안정화 및 Real E2E 검증
- KRX 접속 정상화 확인 후 최종 실데이터 기반 통합 사이클 검증.
- 주요 확인 사항: 데이터 재수집 방지(`price_map`), 분석 품질, 최종 Report 생성물.

### 2. 운영 환경 배포
- 실환경 배포를 위한 Windows Task Scheduler 등록 및 모니터링 체계 구축.
- 자동 로그 수집 및 장애 알림 설정.



## Development Rules
- **DB 보호**: `data/trading.db`를 임의로 삭제/초기화하지 않음. 데이터 분석 후 최소 수정.
- **Real API 보호**: 불필요한 Real API 호출 금지. 최종 검증에 필요한 최소 횟수만 사용.
- **결과 검증**: Mock PASS ≠ Real API PASS ≠ Real E2E PASS 엄격 구분.
- **원인 분석**: [확인]/[추정]/[예정] 구분 명시.
