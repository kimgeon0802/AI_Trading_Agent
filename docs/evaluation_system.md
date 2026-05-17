# 평가 시스템

# 목적

이 문서는 AI 예측 평가 방식을 정의한다.

프로젝트 핵심은
AI의 성공률보다 사고 과정 분석이다.

---

# 평가 흐름

```text
예측 생성
    ↓
일정 기간 경과
    ↓
실제 결과 수집
    ↓
예측 비교
    ↓
실패 원인 분석
```

---

# 평가 항목

반드시 평가해야 하는 요소:

- prediction_accuracy
- confidence_accuracy
- reasoning_quality
- risk_awareness

---

# 평가 예시

```json
{
  "prediction": "BUY",
  "actual_result": "PRICE_DROP",
  "evaluation": "미국 규제 리스크 과소평가",
  "success": false
}
```

---

# 중요 규칙

- 실패 분석 필수
- 성공 분석 필수
- confidence 적절성 평가
- 반복 실패 패턴 추적

---

# 목표

장기적으로:

- AI 판단 패턴 분석
- 시장 상황별 성향 분석
- confidence 신뢰도 분석
- 실패 유형 분석

수행