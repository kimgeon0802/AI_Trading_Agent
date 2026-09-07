import json
import logging

class ResponseParser:
    @staticmethod
    def parse_decision(response_text):
        try:
            data = json.loads(response_text)
            required_fields = ["decision", "confidence", "reasoning", "risks", "expected_result"]
            
            for field in required_fields:
                if field not in data:
                    logging.error(f"Missing required field in AI response: {field}")
                    return None
            
            # Validate decision type
            if data["decision"] not in ["BUY", "SELL", "HOLD"]:
                logging.error(f"Invalid decision type: {data['decision']}")
                return None
                
            return data
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error parsing response: {e}")
            return None
