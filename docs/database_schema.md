# 데이터베이스 스키마

이 문서는 SQLite 데이터베이스 구조를 정의합니다. 모든 AI 판단, 거래, 성과는 이 스키마를 통해 저장됩니다.

---

## 1. trades 테이블
거래 기록 저장. `prediction_id`를 통해 예측과 연동됩니다.

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ticker TEXT,
    decision TEXT,
    quantity INTEGER,
    price REAL,
    confidence REAL,
    prediction_id INTEGER
);
```

## 2. predictions 테이블
AI 예측 기본 정보 저장.

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

## 3. agent_decisions 테이블
Multi-AI 각 모델별 상세 결정 저장.

```sql
CREATE TABLE agent_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER,
    timestamp TEXT,
    model_name TEXT,
    decision TEXT,
    confidence REAL,
    reasoning TEXT,
    risk_assessment TEXT
);
```

## 4. evaluation_logs 테이블
최종 예측에 대한 평가 결과 저장.

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

## 5. portfolio 및 holdings 테이블
가상 계좌 상태 관리.

```sql
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cash REAL,
    total_asset REAL,
    timestamp TEXT
);

CREATE TABLE holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    quantity INTEGER,
    average_price REAL
);
```

## 6. 기타 (reasoning_logs, market_logs, macro_indicators)
보조 로그 및 지표 데이터.
