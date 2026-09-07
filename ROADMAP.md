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

# Phase 3 — 멀티 AI 구조 [진행 중 - 2026-09-07]

목표:
- GPT와 Claude의 독립적인 투자 분석
- GPT/Claude 분석 결과의 Consensus 기반 최종 투자 판단
- AI별 투자 판단 및 성과 분석 기반 마련
- Gemini를 Development / Maintenance AI로 활용하는 구조 설계

진행사항 (2026-09-07):
1. 기존 Gemini 투자 분석 Agent 구현 후 역할 재정의 완료.
2. Gemini는 Trading Intelligence Layer에서 제외, Development / Maintenance Layer로 전환.
3. 실제 투자 판단 AI는 GPT와 Claude로 구성 확정.
4. ConsensusManager를 GPT/Claude 2개 AI 구조에 맞게 재설계 및 구현 완료.
5. 기존 Phase 1/2 기능 및 테스트 정상 확인.

Consensus 설계:
- GPT와 Claude의 decision이 일치하면 해당 decision을 우선한다.
- decision이 다르면 confidence를 기준으로 더 높은 쪽을 선택한다.
- 하나의 AI가 실패하면 정상 응답한 AI의 판단을 사용한다.
- 모든 AI가 실패하면 안전한 HOLD 전략을 사용한다.

DB 설계:
`agent_decisions` 테이블 (기존 테이블 유지, 추가 방식):
- id, prediction_id, timestamp, model_name, decision, confidence, reasoning, risk_assessment

구현 원칙:
- 기존 Phase 1/2 테스트가 계속 통과하도록 regression 유지.
- 대규모 리팩토링 금지, 계층 추가 방식의 구현.

남은 작업:
1. MultiAI Orchestrator 구현 및 RuntimeExecutor 연결
2. RuntimeExecutor 연결 후 E2E 테스트
3. Gemini를 활용한 Development / Maintenance 지원 기능 설계 (Phase 4 연계)