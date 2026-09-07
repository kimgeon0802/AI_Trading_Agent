# AI Trading Agent

## 프로젝트 개요

이 프로젝트는 Multi-AI 기반 가상 투자 연구 시스템입니다.

단순 수익 창출이나 자동매매가 아닌, AI의 시장 해석 논리, 투자 결정 과정, 데이터 중요도, 예측 성공/실패 원인을 연구합니다.

주요 특징:
- **Multi-AI Trading Architecture**: GPT, Claude를 활용한 Consensus 기반 판단
- **Safe Fallback**: API 장애 시 HOLD Fallback 처리
- **Prediction-to-Trade Traceability**: prediction_id를 통한 예측-거래-성과 추적
- **Comprehensive Reporting**: 상세 거래 보고서 및 AI 연구 보고서 자동 생성
- **Virtual Environment**: 가상 계좌 시스템 (실거래 불가)

---

# 프로젝트 구조

```text
agents/          # Multi-AI Agent 로직
data/            # DB (trading.db), 보고서(reports/)
docs/            # 상세 문서
prompts/         # AI 프롬프트
runtime/         # 실행 및 관리(executor, tool_manager)
tests/           # 테스트
```

---

# 현재 개발 상태 (Current Status)

- **Phase 1 (Completed)**: 가상 계좌 시스템, GPT 기반 투자 판단, 뉴스 분석, BUY/SELL/HOLD 결정, 사고 로그 저장.
- **Phase 2 (Completed)**: Multi-AI Orchestrator 도입, API 에러 핸들링, Prediction Traceability(prediction_id).
- **Phase 3 (Current)**: 상세 거래 보고서 및 AI 연구 보고서 자동 생성.

---

# 중요 개발 규칙

- Python 내부에 투자 전략 로직을 넣지 않는다.
- 모든 투자 판단은 AI가 수행한다.
- 모든 AI 응답은 JSON 구조를 사용한다.
- 모든 사고 과정은 로그로 저장한다.
- 모든 거래 및 평가는 `prediction_id`를 기반으로 추적한다.
- 실제 증권 API 연동은 금지한다.