# 평가 프롬프트

과거 투자 예측과 실제 결과를 비교 분석하라.

---

# 목적

이 프롬프트의 목적은
AI의 예측 성공 여부보다
사고 과정의 강점과 약점을 분석하는 것이다.

---

# 반드시 수행할 작업

1. 예측 결과 비교
2. 실패 원인 분석
3. 성공 원인 분석
4. confidence 적절성 평가
5. 리스크 평가 정확성 분석

---

# 중요 규칙

- 단순 성공/실패 판정 금지
- 반드시 원인 분석 수행
- 시장 상황 변화 고려
- hindsight bias 최소화

---

# 분석 대상

- prediction
- actual_result
- reasoning
- risks
- confidence

---

# 출력 형식

반드시 JSON 사용

---

# 출력 예시

```json
{
  "result": "FAIL",
  "failure_reason": [
    "미국 반도체 규제 확대를 충분히 반영하지 못함"
  ],
  "confidence_evaluation": "confidence가 실제 대비 과도하게 높았음",
  "risk_analysis": [
    "정책 리스크 반영 부족"
  ],
  "improvement_points": [
    "거시경제 이벤트 비중 확대 필요"
  ]
}
```