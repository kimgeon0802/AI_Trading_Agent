# 개발 로드맵

# Phase 1 — MVP [완료 - 2024-09-04]

목표:

- 가상 계좌 시스템
- GPT 투자 판단
- 뉴스 분석
- BUY / SELL / HOLD
- SQLite 저장
- 사고 로그 저장

제한사항:

- 멀티 AI 미구현
- 브라우저 자동화 금지
- 실거래 금지

---

# Phase 2 — 분석 고도화 [완료 - 2026-09-04]

목표:

- 감성 분석
- 리스크 평가
- 환율/금리 반영
- confidence 개선
- 평가 시스템 개선

---

# 개발 로드맵

# Phase 1 — MVP [완료 - 2024-09-04]
(생략)

---

# Phase 2 — 분석 고도화 [완료 - 2026-09-04]
(생략)

---

# Phase 3 — 멀티 AI 구조 및 추적성 확보 [완료 - 2026-09-07]

목표:
- Multi-AI (GPT + Claude) Consensus 구조 구현
- `prediction_id` 기반 Traceability 확보
- 상세 거래 보고서(Detailed Trading Report) 구현
- AI Research Report 기반 마련

진행사항:
1. Multi-AI Consensus 구조 및 Orchestrator 구현 완료.
2. `prediction_id` 기반의 `predictions` - `agent_decisions` - `reasoning_logs` - `trades` - `evaluation_logs` 데이터 연결 체계 확립.
3. `cursor.lastrowid` 적용으로 ID 무결성 보장.
4. `Detailed Trading Report` 구현 (포트폴리오 요약, 거래 내역, 자산 구성 시각화).
5. 실제 API 연동 E2E 테스트 및 데이터 일치성 검증 완료.

---

# Phase 4 — 연구 보고서 고도화 [진행 중]

목표:
- 실제 AI 판단 데이터를 기반으로 한 AI Research Report 자동 생성
- GPT vs Claude 성과 비교 분석 체계 구축

진행할 내용:
1. AI Research Report 데이터 쿼리 및 분석 로직 구현.
2. 각 AI 판단 데이터와 실거래 ROI 상관관계 분석.