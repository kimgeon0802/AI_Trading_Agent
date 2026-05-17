# 데이터베이스 스키마

# 목적

이 문서는 SQLite 데이터베이스 구조를 정의한다.

모든 AI 판단 및 로그는 저장되어야 한다.

---

# trades 테이블

가상 거래 기록 저장

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ticker TEXT,
    decision TEXT,
    quantity INTEGER,
    price REAL,
    confidence REAL
);
```

---

# predictions 테이블

AI 예측 저장

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ticker TEXT,
    prediction TEXT,
    expected_return REAL,
    confidence REAL,
    reasoning TEXT
);
```

---

# reasoning_logs 테이블

AI 사고 과정 저장

```sql
CREATE TABLE reasoning_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    decision TEXT,
    reasoning TEXT,
    risks TEXT,
    confidence REAL
);
```

---

# evaluation_logs 테이블

예측 평가 결과 저장

```sql
CREATE TABLE evaluation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    prediction_id INTEGER,
    actual_result TEXT,
    evaluation TEXT,
    success BOOLEAN
);
```

---

# market_logs 테이블

시장 데이터 저장

```sql
CREATE TABLE market_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    market_data TEXT
);
```