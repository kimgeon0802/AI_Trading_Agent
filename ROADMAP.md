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

# Phase 3 — 멀티 AI 구조 [설계 완료 / 구현 대기 - 2026-09-04]

목표:
- GPT, Gemini, Claude 3개 AI 독립적 시장 분석
- Multi-AI 교차 검증 시스템(Consensus) 구축
- 상세 로그를 통한 AI별 성과 분석 기반 마련

진행사항 (2026-09-04):
1. 현재 프로젝트의 기존 GPTAgent 단일 구조 분석 완료.
2. Phase 3 Multi-AI 아키텍처 설계 완료.
3. BaseTradingAgent 추상화 계층 도입 예정.
4. GPT / Gemini / Claude 독립 분석 구조 설계.
5. Multi-AI Orchestrator 및 Consensus 구조 설계.
6. AI별 판단 결과를 저장하기 위한 `agent_decisions` 테이블 추가 예정.
7. Mock AI 기반 Phase 3 전체 파이프라인부터 구현 예정.
8. 실제 AI API 연동은 Mock 파이프라인 검증 이후 진행 예정.
9. ECOS 실제 통계코드 매핑은 아직 미완료이며 Fallback 기반으로 유지 중.
10. 기존 Phase 1/2 기능 및 테스트는 현재 정상.

Consensus 설계:
- 동일한 decision이 과반수이면 해당 decision을 우선한다.
- decision이 모두 다르면 confidence와 risk를 이용하여 결정한다.
- AI 하나가 실패하면 정상 응답한 AI만으로 Consensus를 수행한다.
- 모든 AI가 실패하면 기존 Fallback/안전한 HOLD 전략을 사용한다.
- `confidence`와 `risk_assessment`의 구체적인 점수화 규칙은 구현 단계에서 확정한다.

DB 설계:
`agent_decisions` 테이블 (기존 테이블 유지, 추가 방식):
- id, prediction_id, timestamp, model_name, decision, confidence, reasoning, risk_assessment

구현 원칙:
- 기존 Phase 1/2 테스트가 계속 통과하도록 regression 유지.
- 대규모 리팩토링 금지, 계층 추가 방식의 구현.

내일 구현 작업 순서:
1. BaseTradingAgent
2. GPT Agent Adapter/호환성 구현
3. Gemini Mock Agent
4. Claude Mock Agent
5. ConsensusManager
6. MultiAI Orchestrator
7. agent_decisions DB 저장
8. RuntimeExecutor 연결
9. Mock E2E
10. Phase 1/2 Regression
11. 실제 Gemini/Claude API 연동
12. 실제 Multi-AI E2E

---

# Phase 4 — 자율 리서치 에이전트

목표:

- 브라우저 자동화
- 자율 정보 탐색
- 장기 기억 시스템
- Vector DB
- 자동 리서치 루프