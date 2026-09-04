import os
import logging
import requests
from datetime import datetime
import random
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MacroManager")

class MacroManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.api_key = os.getenv("MACRO_DATA_API_KEY")
        # ECOS API endpoints (Examples)
        # In actual implementation, these need to be constructed with the API key
        self.interest_rate_url = "https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/1/010Y002/Q/20260904/20260904/0101000/"
        self.exchange_rate_url = "https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/1/772Y001/D/20260904/20260904/0000001/"
        self.timeout = 5 # seconds

    def _get_mock_data(self):
        return {"exchange_rate": 1350.0, "interest_rate": 3.5}

    def fetch_and_save_macro_data(self):
        """Fetches macro data and saves to DB. Uses mock on failure."""
        logger.info("Fetching macroeconomic data...")
        
        if not self.api_key:
            logger.warning("MACRO_DATA_API_KEY not set. Using mock data.")
            data = self._get_mock_data()
        else:
            try:
                data = self._fetch_from_api()
            except Exception as e:
                logger.warning(f"Failed to fetch macro data from API: {e}. Using mock data.")
                data = self._get_mock_data()
            
        timestamp = datetime.now().isoformat()
        for key, value in data.items():
            self.db.save_macro_data(key, value, timestamp)
            logger.info(f"Saved {key}: {value}")
            
        return data

    def _fetch_from_api(self):
        # NOTE: This is a structural implementation based on ECOS API requirements.
        # Ensure API_KEY is set in environment.
        
        # 1. Fetch Interest Rate
        int_resp = requests.get(self.interest_rate_url.format(key=self.api_key), timeout=self.timeout)
        int_resp.raise_for_status()
        int_data = int_resp.json()
        
        # 2. Fetch Exchange Rate
        ex_resp = requests.get(self.exchange_rate_url.format(key=self.api_key), timeout=self.timeout)
        ex_resp.raise_for_status()
        ex_data = ex_resp.json()
        
        # Extract values (Assuming valid JSON structure from ECOS)
        # These keys need to be adapted based on actual ECOS API response format
        interest_rate = float(int_data['StatisticSearch']['row'][0]['DATA_VALUE'])
        exchange_rate = float(ex_data['StatisticSearch']['row'][0]['DATA_VALUE'])
        
        return {"exchange_rate": exchange_rate, "interest_rate": interest_rate}

    def get_current_macro_indicators(self):
        return self.db.get_latest_macro_data()
