# 투자 판단 프롬프트

현재 시장 데이터를 기반으로 투자 판단을 수행하라.

---

# 반드시 수행할 작업

1. 시장 상황 분석
2. 뉴스 영향 분석
3. 리스크 평가
4. 투자 판단 수행
5. 판단 이유 설명
6. 예상 결과 설명

---

# 투자 판단 유형

다음 중 하나만 선택 가능:

- BUY
- SELL
- HOLD

---

# 판단 규칙

## BUY

다음 조건일 경우 가능:

- 시장 흐름 긍정적
- 뉴스 긍정적
- 리스크 낮음
- confidence 높음

---

## SELL

다음 조건일 경우 가능:

- 악재 발생
- 리스크 증가
- 시장 약세
- confidence 감소

---

## HOLD

다음 상황에서는 HOLD 우선:

- 데이터 부족
- 방향성 불명확
- 리스크 과도
- confidence 낮음

---

# confidence 규칙

confidence 범위:

0.0 ~ 1.0

예시:

- 0.2 → 매우 낮음
- 0.5 → 중립
- 0.8 → 높은 확신

---

# 반드시 포함해야 하는 항목

- decision
- confidence
- reasoning
- risks
- expected_result

---

# 출력 예시

```json
{
  "decision": "BUY",
  "confidence": 0.74,
  "reasoning": [
    "반도체 업황 회복 기대",
    "외국인 순매수 증가"
  ],
  "risks": [
    "미국 규제 확대 가능성"
  ],
  "expected_result": "1주일 내 상승 가능성"
}
```