import random

class SentimentAnalyzer:
    """
    Simulates sentiment analysis for news articles.
    In Phase 2, this provides a structured way to score news.
    """
    def __init__(self):
        self.positive_keywords = ["상승", "호재", "흑자", "성장", "강세", "회복", "매수", "이익", "증가"]
        self.negative_keywords = ["하락", "악재", "적자", "둔화", "약세", "위기", "매도", "손실", "감소"]

    def analyze_text(self, text):
        score = 0.0
        for word in self.positive_keywords:
            if word in text:
                score += 0.2
        for word in self.negative_keywords:
            if word in text:
                score -= 0.2
        
        # Clamp between -1.0 and 1.0
        score = max(-1.0, min(1.0, score))
        
        # Add a bit of randomness to simulate complex AI analysis
        score += random.uniform(-0.1, 0.1)
        score = round(max(-1.0, min(1.0, score)), 2)
        
        if score > 0.3:
            label = "Positive"
        elif score < -0.3:
            label = "Negative"
        else:
            label = "Neutral"
            
        return {
            "score": score,
            "label": label
        }

    def analyze_news_list(self, news_list):
        if not news_list:
            return {"average_score": 0.0, "label": "Neutral", "details": []}
            
        details = []
        total_score = 0.0
        
        for news in news_list:
            analysis = self.analyze_text(news.get("title", "") + " " + news.get("summary", ""))
            details.append({
                "title": news.get("title"),
                "sentiment": analysis
            })
            total_score += analysis["score"]
            
        avg_score = round(total_score / len(news_list), 2)
        
        if avg_score > 0.3:
            avg_label = "Positive"
        elif avg_score < -0.3:
            avg_label = "Negative"
        else:
            avg_label = "Neutral"
            
        return {
            "average_score": avg_score,
            "label": avg_label,
            "details": details
        }
