# 데이터 구조 정의

# 목적

이 문서는 GPT에게 전달되는 데이터 구조를 정의한다.

모든 데이터는 구조화된 JSON 형태로 전달해야 한다.

Python은 데이터를 수집 및 정리만 수행하며,
해석 및 판단은 AI가 수행한다.

---

# 전체 데이터 구조

```json
{
  "timestamp": "",
  "market_summary": {},
  "macro_data": {},
  "portfolio": {},
  "watchlist": [],
  "news": [],
  "technical_indicators": {},
  "previous_predictions": []
}
```

---

# market_summary

시장 전체 흐름 정보

예시:

```json
{
  "kospi": 0.8,
  "nasdaq": -1.2,
  "usdkrw": 1382.5,
  "fear_greed_index": 42
}
```

---

# macro_data

거시경제 데이터

예시:

```json
{
  "interest_rate": 3.5,
  "cpi": 2.3,
  "oil_price": 78.1
}
```

---

# portfolio

현재 가상 계좌 상태

예시:

```json
{
  "cash": 1000000,
  "total_asset": 1000000,
  "holdings": []
}
```

---

# news

뉴스 리스트

예시:

```json
[
  {
    "title": "미국 반도체 규제 강화",
    "source": "Reuters",
    "summary": "중국 반도체 수출 규제 확대",
    "published_at": "2026-05-17"
  }
]
```

---

# technical_indicators

기술적 지표

예시:

```json
{
  "005930": {
    "rsi": 48,
    "macd": -0.3,
    "moving_average_20": 71000
  }
}
```

---

# previous_predictions

과거 예측 기록

예시:

```json
[
  {
    "ticker": "005930",
    "decision": "BUY",
    "confidence": 0.72,
    "result": "FAIL"
  }
]
```