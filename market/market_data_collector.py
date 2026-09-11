import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pykrx import stock
from market.screening_engine import ScreeningEngine


# ============================================================
# Project Path Configuration
# ============================================================

# market/market_data_collector.py
#        ↓
# 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Environment Configuration
# ============================================================

ENV_FILE = PROJECT_ROOT / ".env"

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f".env 파일을 찾을 수 없습니다: {ENV_FILE}"
    )

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


import logging

logger = logging.getLogger("MarketDataCollector")

class MarketDataCollector:
    """
    KOSPI + KOSDAQ 전체 시장 데이터를 수집하는 클래스.

    수집 범위
    ----------
    1. 종목 기본 정보
    2. 가격 정보
    3. 거래량 / 거래대금
    4. 시가총액
    5. 상장주식수
    """

    def __init__(self):
        self.collected_at = None
        self.MAX_LOOKBACK_DAYS = 10

        self.krx_id = os.getenv("KRX_ID")
        self.krx_pw = os.getenv("KRX_PW")

        self._validate_krx_credentials()

    # ========================================================
    # KRX Credential Validation
    # ========================================================

    def _validate_krx_credentials(self):
        """
        KRX 로그인 환경변수 로드 여부를 확인한다.

        실제 ID / PW는 출력하지 않는다.
        """

        if not self.krx_id:
            raise RuntimeError(
                "KRX_ID 환경 변수가 설정되지 않았습니다."
            )

        if not self.krx_pw:
            raise RuntimeError(
                "KRX_PW 환경 변수가 설정되지 않았습니다."
            )

        print("[OK] KRX_ID 로드 확인")
        print("[OK] KRX_PW 로드 확인")

    # ========================================================
    # Date
    # ========================================================

    def get_request_date(self):
        """
        현재 날짜를 pykrx 요청용 YYYYMMDD 형식으로 반환한다.
        """

        return datetime.now().strftime("%Y%m%d")

    def _get_valid_trading_days(self):
        """
        최근 거래일 목록을 가져온다.
        """
        # 현재 날짜 기준 최근 2개월의 거래일을 가져와서 충분한 후보군 확보
        today = datetime.now()
        
        # 현재 달과 이전 달을 포함
        dates = []
        for i in range(2):
            target_date = today - timedelta(days=i*30)
            dates.extend(stock.get_previous_business_days(year=target_date.year, month=target_date.month))
        
        # 중복 제거 및 정렬
        sorted_dates = sorted(list(set(dates)))
        return sorted_dates

    def _is_data_valid(self, df: pd.DataFrame) -> bool:
        """
        수집된 데이터가 유효한지 검증한다.
        """
        if df.empty:
            return False
        
        # 중요 가격/시가총액 데이터가 모두 0이면 유효하지 않음으로 간주
        critical_cols = ['close', 'market_cap']
        if all(col in df.columns for col in critical_cols):
            if (df[critical_cols] == 0).all().all():
                return False
        
        return True

    # ========================================================
    # Ticker List
    # ========================================================

    def get_market_tickers(
        self,
        market: str,
        request_date: str
    ):
        """
        특정 시장의 전체 종목 코드를 조회한다.
        """

        print(
            f"[INFO] {market} 종목 목록 조회 중..."
        )

        tickers = stock.get_market_ticker_list(
            date=request_date,
            market=market
        )

        if not tickers:
            raise RuntimeError(
                f"{market} 종목 목록을 가져오지 못했습니다."
            )

        return tickers

    # ========================================================
    # Basic Information
    # ========================================================

    def get_basic_dataframe(
        self,
        market: str,
        request_date: str
    ):
        """
        종목 코드 / 종목명 / 시장 정보를 생성한다.
        """

        tickers = self.get_market_tickers(
            market,
            request_date
        )

        data = []

        for index, ticker in enumerate(
            tickers,
            start=1
        ):

            name = stock.get_market_ticker_name(
                ticker
            )

            data.append(
                {
                    "ticker": ticker,
                    "name": name,
                    "market": market,
                }
            )

            if index % 100 == 0:

                print(
                    f"[INFO] {market} 기본 정보 "
                    f"{index}/{len(tickers)}"
                )

        return pd.DataFrame(data)

    # ========================================================
    # Market OHLCV
    # ========================================================

    def get_market_ohlcv(
        self,
        market: str,
        request_date: str
    ):
        """
        특정 시장 전체 종목의
        OHLCV 데이터를 조회한다.

        반환 컬럼
        ----------
        ticker
        open
        high
        low
        close
        volume
        trading_value
        change
        """

        print(
            f"[INFO] {market} OHLCV 조회 중..."
        )

        df = stock.get_market_ohlcv_by_ticker(
            request_date,
            market=market
        )

        if df.empty:
            raise RuntimeError(
                f"{market} OHLCV 데이터를 가져오지 못했습니다."
            )

        df = df.reset_index()

        # pykrx의 index 컬럼을 ticker로 변경
        df = df.rename(
            columns={
                "티커": "ticker",
                "시가": "open",
                "고가": "high",
                "저가": "low",
                "종가": "close",
                "거래량": "volume",
                "거래대금": "trading_value",
                "등락률": "change_rate",
            }
        )

        # 전일 대비 가격 변화 계산
        df["change"] = (
            df["close"]
            - (
                df["close"]
                /
                (1 + df["change_rate"] / 100)
            )
        )

        return df[
            [
                "ticker",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "trading_value",
                "change",
                "change_rate",
            ]
        ]

    # ========================================================
    # Market Capitalization
    # ========================================================

    def get_market_cap(
        self,
        market: str,
        request_date: str
    ):
        """
        특정 시장 전체 종목의
        시가총액 / 상장주식수 데이터를 조회한다.
        """

        print(
            f"[INFO] {market} 시가총액 조회 중..."
        )

        df = stock.get_market_cap_by_ticker(
            request_date,
            market=market
        )

        if df.empty:
            raise RuntimeError(
                f"{market} 시가총액 데이터를 가져오지 못했습니다."
            )

        df = df.reset_index()

        df = df.rename(
            columns={
                "티커": "ticker",
                "시가총액": "market_cap",
                "상장주식수": "shares",
            }
        )

        return df[
            [
                "ticker",
                "market_cap",
                "shares",
            ]
        ]

    # ========================================================
    # Historical OHLCV
    # ========================================================

    def get_historical_ohlcv(self, ticker: str, days: int = 100) -> pd.DataFrame:
        """
        특정 종목의 과거 OHLCV 데이터를 조회한다.
        """
        # 현재 날짜로부터 days만큼 이전 날짜 계산
        # 거래일 기준이 아니므로 넉넉하게 잡기 위해 1.5배의 캘린더 일수 사용
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days * 1.5)
        
        print(f"[INFO] Fetching historical data for {ticker}: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        
        df = stock.get_market_ohlcv(
            start_date.strftime("%Y%m%d"),
            end_date.strftime("%Y%m%d"),
            ticker
        )
        
        if df.empty:
            logger.warning(f"No historical data for {ticker}")
            return pd.DataFrame()
            
        df = df.reset_index()
        
        # 컬럼 표준화
        df = df.rename(
            columns={
                "날짜": "date",
                "시가": "open",
                "고가": "high",
                "저가": "low",
                "종가": "close",
                "거래량": "volume",
                "등락률": "change_rate",
            }
        )
        
        # 필요한 컬럼만 선택 및 정렬
        df = df[["date", "open", "high", "low", "close", "volume", "change_rate"]]
        df = df.sort_values(by="date", ascending=True)
        
        return df
    # ========================================================

    def collect_market(
        self,
        market: str,
        request_date: str
    ):
        """
        하나의 시장 데이터를 수집하고 통합한다.
        """

        print()
        print(
            f"[INFO] =================================="
        )

        print(
            f"[INFO] {market} 데이터 수집 시작"
        )

        print(
            f"[INFO] =================================="
        )

        basic_df = self.get_basic_dataframe(
            market,
            request_date
        )

        ohlcv_df = self.get_market_ohlcv(
            market,
            request_date
        )

        market_cap_df = self.get_market_cap(
            market,
            request_date
        )

        # 기본 정보 + OHLCV
        result_df = basic_df.merge(
            ohlcv_df,
            on="ticker",
            how="left"
        )

        # + 시가총액
        result_df = result_df.merge(
            market_cap_df,
            on="ticker",
            how="left"
        )

        print(
            f"[INFO] {market} 데이터 수집 완료: "
            f"{len(result_df)}개"
        )

        return result_df

    # ========================================================
    # All Markets Collection
    # ========================================================

    def collect_all_markets(self):
        """
        KOSPI + KOSDAQ 전체 시장 데이터를 수집한다.
        최신 유효 거래일 데이터를 수집한다.
        """

        requested_date = self.get_request_date()
        valid_trading_days = self._get_valid_trading_days()
        
        print(f"[INFO] Requested data date: {requested_date}")
        
        # 최신 거래일부터 역순으로 조회
        for target_date_ts in reversed(valid_trading_days):
            target_date = target_date_ts.strftime("%Y%m%d")
            
            print(f"[INFO] Trying to collect data for: {target_date}")
            
            try:
                kospi_df = self.collect_market("KOSPI", target_date)
                kosdaq_df = self.collect_market("KOSDAQ", target_date)
                
                market_df = pd.concat([kospi_df, kosdaq_df], ignore_index=True)
                
                if self._is_data_valid(market_df):
                    self.collected_at = datetime.now()
                    market_df["data_date"] = target_date
                    market_df["collected_at"] = self.collected_at.isoformat()
                    
                    # Log status
                    print(f"[INFO] Data validation: SUCCESS")
                    print(f"[INFO] Actual data date: {target_date}")
                    print(f"[INFO] Data status: {'CURRENT' if target_date == requested_date else 'FALLBACK_CONFIRMED'}")
                    
                    # 컬럼 순서 통일
                    return market_df[[
                        "ticker", "name", "market", "open", "high", "low", "close",
                        "change", "change_rate", "volume", "trading_value",
                        "market_cap", "shares", "data_date", "collected_at"
                    ]]
                else:
                    print(f"[WARNING] Data validation failed for: {target_date}")
            
            except Exception as e:
                print(f"[ERROR] Failed to collect data for {target_date}: {e}")

        raise RuntimeError("최근 유효한 시장 데이터를 찾을 수 없습니다.")


# ============================================================
# Main
# ============================================================

def main():
    collector = MarketDataCollector()

    market_df = collector.collect_all_markets()

    screening_engine = ScreeningEngine()

    candidates = screening_engine.run(
        market_df
    )

    print("========================================")
    print(" AI Trading Agent")
    print(" Market Data Collector")
    print("========================================")

    print(
        f"Project Root : "
        f"{PROJECT_ROOT}"
    )

    print(
        f".env File    : "
        f"{ENV_FILE}"
    )

    print("----------------------------------------")

    collector = MarketDataCollector()

    print("----------------------------------------")

    market_df = collector.collect_all_markets()

    print()
    print("========================================")
    print(" 전체 시장 데이터 수집 결과")
    print("========================================")

    print(
        market_df.head(20).to_string()
    )

    print()
    print("========================================")
    print(" 시장별 종목 수")
    print("========================================")

    print(
        market_df.groupby("market")
        .size()
    )

    print()
    print("========================================")
    print(" 데이터 컬럼")
    print("========================================")

    for column in market_df.columns:

        print(
            f"- {column}"
        )

    print()
    print("========================================")
    print(" 데이터 결측치")
    print("========================================")

    print(
        market_df.isnull().sum()
    )

    print()
    print("========================================")
    print(" 수집 완료")
    print("========================================")

    print(
        f"Data Date    : "
        f"{collector.get_request_date()}"
    )

    print(
        f"Collected At : "
        f"{collector.collected_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        f"Total Stocks : "
        f"{len(market_df)}"
    )

    print("\n========================================")
    print(" 최종 스크리닝 후보 종목")
    print("========================================")

    print(
        candidates[
            [
                "rank",
                "ticker",
                "name",
                "market",
                "close",
                "change_rate",
                "trading_value",
                "market_cap",
                "liquidity_score",
                "momentum_score",
                "market_cap_score",
                "screening_score",
            ]
        ].to_string(
            index=False
        )
    )
    print("========================================")


if __name__ == "__main__":
    main()