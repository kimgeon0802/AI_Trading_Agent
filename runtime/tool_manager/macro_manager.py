import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MacroManager")

class MacroManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.api_key = os.getenv("MACRO_DATA_API_KEY")
        self.base_url = f"https://ecos.bok.or.kr/api/KeyStatisticList/{self.api_key}/json/kr/1/100/"
        self.timeout = 10
        
        # KEYSTAT_NAME -> 내부 필드 매핑
        self.indicator_mapping = {
            "원/달러 환율(종가)": "exchange_rate",
            "한국은행 기준금리": "interest_rate",
            "국고채수익률(3년)": "treasury_yield",
            "소비자물가지수": "cpi",
            "GDP(명목, 계절조정)": "gdp",
            "실업률": "unemployment_rate"
        }

    def _get_mock_value(self, field):
        mock_data = {
            "exchange_rate": 1350.0,
            "interest_rate": 3.5,
            "treasury_yield": 3.5,
            "cpi": 115.0,
            "gdp": 500000.0,
            "unemployment_rate": 2.5
        }
        return mock_data.get(field, 0.0)

    def fetch_and_save_macro_data(self):
        """Fetches macro data and saves to DB. Uses mock on failure per indicator."""
        logger.info("Fetching macroeconomic data from ECOS...")
        
        api_data = {}
        if self.api_key:
            try:
                response = requests.get(self.base_url, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    if "KeyStatisticList" in data and "row" in data["KeyStatisticList"]:
                        api_data = {row["KEYSTAT_NAME"]: row["DATA_VALUE"] for row in data["KeyStatisticList"]["row"]}
                    else:
                        logger.warning("ECOS API returned no valid data (KeyStatisticList/row missing).")
                else:
                    logger.warning(f"ECOS API request failed with status: {response.status_code}")
            except Exception as e:
                logger.warning(f"ECOS API connection error: {e}")
        else:
            logger.warning("MACRO_DATA_API_KEY not set.")
            
        final_data = {}
        timestamp = datetime.now().isoformat()
        
        for key_name, field_name in self.indicator_mapping.items():
            value_str = api_data.get(key_name)
            
            # Numeric 변환 시도
            try:
                if value_str is not None and str(value_str).strip() != "" and str(value_str).strip().upper() != "NULL":
                    value = float(str(value_str).replace(",", ""))
                    logger.info(f"[MACRO] {field_name}={value} source=ECOS")
                    final_data[field_name] = value
                else:
                    raise ValueError("Missing or invalid data")
            except (ValueError, TypeError):
                # Fallback to Mock
                value = self._get_mock_value(field_name)
                logger.warning(f"[MACRO] {field_name}={value} source=MOCK reason=missing_or_invalid_ecos_data")
                final_data[field_name] = value
            
            # DB 저장
            self.db.save_macro_data(field_name, value, timestamp)
            
        return final_data

    def get_current_macro_indicators(self):
        return self.db.get_latest_macro_data()
