# AI 역할 정의

# 목적

이 문서는 멀티 AI 구조의 역할 분리를 정의합니다.

---

# GPT 역할 (1차 판단)

메인 투자 판단 AI

담당:

- 시장 분석
- 1차 투자 판단 (BUY/SELL/HOLD)
- 관계형 추론
- 예측 생성

---

# Claude 역할 (2차 검증)

Critic AI

담당:

- GPT 판단 검증
- 논리 검증
- 리스크 분석 (PASS/WARNING/REJECT)
- 반론 제시

---

# ConsensusManager 역할 (최종 결정)

투자 판단 Gate

담당:

- GPT 판단과 Claude 검증을 결합하여 최종 결정
- API 에러 시 안전한 HOLD Fallback 처리

---

# Gemini 역할 (개발/유지보수)

개발자 전용 Agent

담당:

- 코드 유지보수
- 시스템 분석
- 기능 구현

---

# 중요 원칙

AI는 서로 역할을 침범하지 않으며, ConsensusManager를 통해 최종 결정이 이루어집니다.