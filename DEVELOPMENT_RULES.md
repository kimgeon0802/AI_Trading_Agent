# 개발 규칙

# 핵심 규칙

1. Python은 실행 역할만 담당한다.
2. 투자 판단 로직은 Python에 작성하지 않는다.
3. 모든 투자 판단은 AI가 수행한다.
4. 모든 AI 응답은 JSON 형식이어야 한다.
5. 모든 사고 과정은 저장해야 한다.

---

# 역할 분리 규칙

## Python 역할

- 데이터 수집
- 스케줄 실행
- Tool 호출
- DB 저장
- 로그 저장

Python은 투자 판단을 하지 않는다.

---

## AI 역할

- 시장 분석
- 뉴스 해석
- 투자 판단
- 리스크 평가
- 결과 분석

---

# 금지 사항

- 하드코딩 투자 전략
- 실제 자동매매
- 실거래 API 연결
- JSON 외 자유형 응답
- 숨겨진 투자 규칙 구현

---

# AI 응답 필수 항목

AI는 반드시 아래 항목을 포함해야 한다.

- decision
- confidence
- reasoning
- risks
- expected_result

---

# HOLD 규칙

다음 상황에서는 반드시 HOLD 선택:

- 데이터 부족
- 확신도 부족
- 시장 불확실성 증가

---

# 로그 저장 규칙

모든 AI 행동은 저장해야 한다.

필수 저장 항목:

- timestamp
- input_data
- decision
- confidence
- reasoning
- risks
- prediction