import logging
import os
import json
from datetime import datetime

logger = logging.getLogger("ResearchReportGenerator")

class ResearchReportGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
        self.report_dir = "data/reports/research/"
        self.gemini_log_path = "logs/gemini_batch_output.log"
        os.makedirs(self.report_dir, exist_ok=True)

    def _get_gemini_opinion(self, prediction_timestamp, ticker):
        """
        Gemini 로그에서 특정 시점과 종목에 대한 분석 결과 추출 (최소 시간차 선택).
        """
        if not os.path.exists(self.gemini_log_path):
            return "데이터 없음"
        
        try:
            pred_time = datetime.fromisoformat(prediction_timestamp)
            candidates = []
            
            with open(self.gemini_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    log_entry = json.loads(line)
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    time_diff = abs((pred_time - log_time).total_seconds())
                    
                    if time_diff < 300:
                        for analysis in log_entry.get("analyses", []):
                            if analysis.get("ticker") == ticker:
                                candidates.append({
                                    "time_diff": time_diff,
                                    "log_timestamp": log_entry['timestamp'],
                                    "decision": analysis.get("decision", "데이터 없음")
                                })
            
            if not candidates:
                return "데이터 없음"
            
            # 최소 시간차 찾기
            min_diff = min(c["time_diff"] for c in candidates)
            best_candidates = [c for c in candidates if c["time_diff"] == min_diff]
            
            # 동률 후보 확인
            if len(best_candidates) > 1:
                return "데이터 없음"
                
            return best_candidates[0]["decision"]
            
        except Exception as e:
            logger.warning(f"Error reading Gemini log: {e}")
            return "데이터 없음"

    def _generate_bar_chart(self, data, max_width=20):
        if not data or sum(data.values()) == 0: return "데이터 없음"
        total = sum(data.values())
        chart = ""
        for label, count in data.items():
            bar_width = int((count / total) * max_width)
            percentage = (count / total) * 100
            chart += f"{label:<15} {'█' * bar_width}{'░' * (max_width - bar_width)} {count} ({percentage:.0f}%)\n"
        return chart

    def _fetch_all_data(self):
        query = """
            SELECT
                p.id AS pid, p.ticker, p.timestamp,
                p.prediction AS final_decision,
                c.decision AS claude_val, c.confidence AS claude_score,
                con.decision AS consensus_decision,
                t.id AS trade_id, t.decision AS trade_decision,
                e.success, e.actual_result
            FROM predictions p
            LEFT JOIN agent_decisions c ON p.id = c.prediction_id AND c.model_name = 'claude'
            LEFT JOIN agent_decisions con ON p.id = con.prediction_id AND con.model_name = 'consensus_manager'
            LEFT JOIN trades t ON p.id = t.prediction_id
            LEFT JOIN evaluation_logs e ON p.id = e.prediction_id
            ORDER BY p.timestamp DESC;
        """
        results = self.db.execute_query(query)
        columns = ['pid', 'ticker', 'timestamp', 'final_decision',
                   'claude_val', 'claude_score', 'consensus_decision',
                   'trade_id', 'trade_decision', 'success', 'actual_result']
        
        data = []
        for row in results:
            item = dict(zip(columns, row))
            # Gemini 의견 매핑 추가
            item['gemini_opinion'] = self._get_gemini_opinion(item['timestamp'], item['ticker'])
            data.append(item)
            
        return data

    def _calculate_metrics(self, data):
        # Gemini 의견 기반 지표 계산 로직 유지
        metrics = {
            'gemini': {'BUY': {'total': 0, 'success': 0}, 'SELL': {'total': 0, 'success': 0}, 'HOLD': {'total': 0, 'success': 0}},
            'claude': {'PASS': {'total': 0, 'trades': 0, 'success': 0}, 'WARNING': {'total': 0, 'trades': 0, 'success': 0}, 'REJECT': {'total': 0, 'trades': 0, 'success': 0}}
        }
        
        for r in data:
            if r['gemini_opinion'] in metrics['gemini']:
                metrics['gemini'][r['gemini_opinion']]['total'] += 1
                if r['success'] == 1:
                    metrics['gemini'][r['gemini_opinion']]['success'] += 1
            
            if r['claude_val'] in metrics['claude']:
                metrics['claude'][r['claude_val']]['total'] += 1
                if r['trade_id']:
                    metrics['claude'][r['claude_val']]['trades'] += 1
                    if r['success'] == 1:
                        metrics['claude'][r['claude_val']]['success'] += 1
        return metrics

    def generate_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_path = os.path.join(self.report_dir, f"ai_research_report_{timestamp}.md")
        data = self._fetch_all_data()
        metrics = self._calculate_metrics(data)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# AI 연구 보고서 - {timestamp}\n\n")
            
            # 1. Summary
            f.write("## 1. AI 의사결정 요약\n\n| 항목 | Gemini 1차 의견 | Claude 검증 결과 | 최종 판단 |\n| --- | ---: | ---: | ---: |\n")
            f.write(f"| 매수(BUY) | {sum(1 for r in data if r['gemini_opinion'] == 'BUY')} | - | {sum(1 for r in data if r['final_decision'] == 'BUY')} |\n")
            f.write(f"| 매도(SELL) | {sum(1 for r in data if r['gemini_opinion'] == 'SELL')} | - | {sum(1 for r in data if r['final_decision'] == 'SELL')} |\n")
            f.write(f"| 관망(HOLD) | {sum(1 for r in data if r['gemini_opinion'] == 'HOLD')} | - | {sum(1 for r in data if r['final_decision'] == 'HOLD')} |\n\n")
            
            # 4. Tracking
            f.write("## 2. 상세 의사결정 추적\n\n")
            f.write("| ID | 종목 | Gemini 1차 의견 | Claude 검증 결과 | 최종 판단 | 결과 |\n| --- | --- | --- | --- | --- | --- |\n")
            for r in data:
                f.write(f"| {r['pid']} | {r['ticker']} | {r['gemini_opinion']} | {r['claude_val'] or '-'} | {r['final_decision'] or '-'} | {r['actual_result'] or '데이터 없음'} |\n")
            f.write("\n")
            
        logger.info(f"Research report generated: {report_path}")
        return report_path
