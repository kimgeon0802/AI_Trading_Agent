# Tool Calling 구조

# 목적

이 문서는 GPT와 Python Runtime 간 상호작용 방식을 정의한다.

GPT는 직접 인터넷 접근 및 실행을 하지 않는다.

모든 실행은 Python Runtime이 수행한다.

---

# 기본 흐름

```text
GPT 요청
    ↓
Python Tool 실행
    ↓
결과 반환
    ↓
GPT 분석
```

---

# 뉴스 조회 흐름

```text
GPT:
"삼성전자 최신 뉴스 조회"

↓

Python:
search_news("삼성전자")

↓

뉴스 결과 반환

↓

GPT:
뉴스 분석 수행
```

---

# 주가 조회 흐름

```text
GPT:
"005930 현재 주가 조회"

↓

Python:
get_stock_price("005930")

↓

결과 반환

↓

GPT:
시장 분석 수행
```

---

# Tool 실행 규칙

- GPT는 Tool 목적만 설명한다.
- Python은 실제 실행만 담당한다.
- Python은 투자 판단을 하지 않는다.
- 모든 Tool 결과는 JSON 형태로 반환한다.

---

# 금지 사항

- Python 내부 투자 판단 금지
- GPT 직접 코드 실행 금지
- 자유형 문자열 반환 금지