# 로깅 시스템

# 목적

이 문서는 AI의 사고 과정 저장 규칙을 정의한다.

프로젝트 핵심 목표는
AI의 사고 과정을 관찰하는 것이다.

따라서 모든 판단 과정은 반드시 저장해야 한다.

---

# 저장 대상

반드시 저장해야 하는 항목:

- timestamp
- market_context
- decision
- confidence
- reasoning
- risks
- expected_result

---

# 로그 예시

```json
{
  "timestamp": "2026-05-17T09:00:00",
  "decision": "BUY",
  "ticker": "005930",
  "confidence": 0.71,
  "reasoning": [
    "외국인 순매수 증가",
    "반도체 업황 회복 기대"
  ],
  "risks": [
    "미국 규제 확대 가능성"
  ],
  "expected_result": "1주일 내 상승 가능성"
}
```

---

# 로그 저장 규칙

- 모든 투자 판단 저장
- 모든 실패 분석 저장
- 모든 평가 결과 저장
- 로그 삭제 금지
- 로그 수정 금지

---

# 로그 활용 목적

- AI 사고 분석
- 실패 패턴 분석
- confidence 정확도 분석
- 시장 상황별 행동 분석