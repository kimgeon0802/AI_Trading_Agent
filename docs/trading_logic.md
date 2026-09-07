# 투자 판단 로직

# 목적

이 문서는 AI 투자 판단 기준을 정의합니다.

최종 투자 판단은 **ConsensusManager**가 GPT(1차 판단)와 Claude(2차 검증) 결과를 바탕으로 수행합니다.

Python은 투자 판단을 하지 않으며 오직 실행을 담당합니다.

---

# 기본 판단 유형

AI는 다음 3가지 중 하나를 선택해야 합니다.

- BUY
- SELL
- HOLD

---

# Multi-AI 판단 Flow

1. **Market Data** → **GPTAgent** (1차 판단, Reasoning, Risks, Confidence)
2. **GPT Output** → **ClaudeAgent** (검증, PASS/WARNING/REJECT, Score, Evaluation)
3. **Claude Output** → **ConsensusManager** (최종 판단)

---

# 중요 규칙

- 모든 판단은 `prediction_id` 기반으로 추적됩니다.
- GPT/Claude 응답은 항상 JSON 구조를 사용합니다.
- API 에러 발생 시 ConsensusManager는 HOLD를 선택합니다.
- 데이터 부족 시 HOLD를 우선합니다.