from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("ScreeningEngine")


@dataclass
class ScreeningConfig:
    """
    시장 스크리닝 설정

    현재 MarketDataCollector에서 수집하는
    단일 시점 시장 데이터만 사용하는 1차 스크리닝 설정이다.

    추후 시간별/일별 데이터가 누적되면
    RSI, MACD, 이동평균선, 거래량 증가율 등을 추가할 수 있다.
    """

    # 최소 거래대금
    # 기본값: 10억원
    min_trading_value: int = 1_000_000_000

    # 최소 시가총액
    # 기본값: 500억원
    min_market_cap: int = 50_000_000_000

    # 극단적인 급등/급락 종목 제외 기준
    min_change_rate: float = -10.0
    max_change_rate: float = 15.0

    # 최종 후보 종목 수
    top_n: int = 50

    # 각 점수의 가중치
    liquidity_weight: float = 0.40
    momentum_weight: float = 0.35
    market_cap_weight: float = 0.25


class ScreeningEngine:
    """
    전체 시장 데이터 기반 1차 스크리닝 엔진

    사용 흐름
    --------

    MarketDataCollector
        ↓
    전체 KOSPI + KOSDAQ 데이터
        ↓
    ScreeningEngine
        ↓
    후보 종목 TOP N
        ↓
    GPT Web Search 기반 분석
        ↓
    Claude + RAG 2차 분석
    """

    REQUIRED_COLUMNS = [
        "ticker",
        "name",
        "market",
        "open",
        "high",
        "low",
        "close",
        "change",
        "change_rate",
        "volume",
        "trading_value",
        "market_cap",
        "shares",
        "data_date",
        "collected_at",
    ]

    def __init__(
        self,
        config: Optional[ScreeningConfig] = None
    ):
        """
        Parameters
        ----------
        config : ScreeningConfig, optional
            스크리닝 조건 설정
        """

        self.config = config or ScreeningConfig()

    def validate_market_data(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        MarketDataCollector에서 전달받은 데이터 검증

        Parameters
        ----------
        market_df : pd.DataFrame
            전체 시장 데이터

        Returns
        -------
        pd.DataFrame
            검증 및 정리된 시장 데이터
        """

        logger.info(
            "Validating market data..."
        )

        if market_df is None:
            raise ValueError(
                "Market data is None."
            )

        if market_df.empty:
            raise ValueError(
                "Market data is empty."
            )

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in market_df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                f"{missing_columns}"
            )

        df = market_df.copy()

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "change",
            "change_rate",
            "volume",
            "trading_value",
            "market_cap",
            "shares",
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # 가격이 0 이하인 종목 제거
        df = df[
            df["close"] > 0
        ]

        # 거래량이 음수인 데이터 제거
        df = df[
            df["volume"] >= 0
        ]

        # 시가총액이 0 이하인 종목 제거
        df = df[
            df["market_cap"] > 0
        ]

        # 거래대금이 음수인 데이터 제거
        df = df[
            df["trading_value"] >= 0
        ]

        # 필수 데이터 결측치 제거
        required_numeric_columns = [
            "close",
            "change_rate",
            "volume",
            "trading_value",
            "market_cap",
        ]

        df = df.dropna(
            subset=required_numeric_columns
        )

        df = df.reset_index(
            drop=True
        )

        logger.info(
            "Market data validation completed: "
            f"{len(df)} stocks"
        )

        return df

    def filter_liquidity(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        거래대금 기반 유동성 필터

        너무 거래가 적은 종목을 제거한다.

        Parameters
        ----------
        market_df : pd.DataFrame

        Returns
        -------
        pd.DataFrame
        """

        before_count = len(
            market_df
        )

        filtered_df = market_df[
            market_df["trading_value"]
            >= self.config.min_trading_value
        ].copy()

        after_count = len(
            filtered_df
        )

        logger.info(
            "Liquidity filter: "
            f"{before_count} -> {after_count}"
        )

        return filtered_df

    def filter_market_cap(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        시가총액 기반 필터

        지나치게 작은 기업을 제거한다.

        Parameters
        ----------
        market_df : pd.DataFrame

        Returns
        -------
        pd.DataFrame
        """

        before_count = len(
            market_df
        )

        filtered_df = market_df[
            market_df["market_cap"]
            >= self.config.min_market_cap
        ].copy()

        after_count = len(
            filtered_df
        )

        logger.info(
            "Market cap filter: "
            f"{before_count} -> {after_count}"
        )

        return filtered_df

    def filter_extreme_change(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        극단적인 급등/급락 종목 제거

        당일 지나치게 급등하거나 급락한 종목은
        초기 스크리닝 단계에서 제외한다.

        추후 전략에 따라 설정값을 변경할 수 있다.

        Parameters
        ----------
        market_df : pd.DataFrame

        Returns
        -------
        pd.DataFrame
        """

        before_count = len(
            market_df
        )

        filtered_df = market_df[
            (
                market_df["change_rate"]
                >= self.config.min_change_rate
            )
            &
            (
                market_df["change_rate"]
                <= self.config.max_change_rate
            )
        ].copy()

        after_count = len(
            filtered_df
        )

        logger.info(
            "Extreme change filter: "
            f"{before_count} -> {after_count}"
        )

        return filtered_df

    @staticmethod
    def normalize_series(
        series: pd.Series
    ) -> pd.Series:
        """
        0 ~ 100 범위로 Min-Max 정규화

        Parameters
        ----------
        series : pd.Series

        Returns
        -------
        pd.Series
        """

        minimum = series.min()
        maximum = series.max()

        if pd.isna(
            minimum
        ) or pd.isna(
            maximum
        ):
            return pd.Series(
                0.0,
                index=series.index
            )

        if maximum == minimum:
            return pd.Series(
                50.0,
                index=series.index
            )

        normalized = (
            (
                series - minimum
            )
            /
            (
                maximum - minimum
            )
            * 100
        )

        return normalized

    def calculate_liquidity_score(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        유동성 점수 계산

        평가 요소
        --------
        - 거래대금
        - 거래량

        Returns
        -------
        pd.DataFrame
        """

        df = market_df.copy()

        trading_value_score = (
            self.normalize_series(
                np.log1p(
                    df["trading_value"]
                )
            )
        )

        volume_score = (
            self.normalize_series(
                np.log1p(
                    df["volume"]
                )
            )
        )

        df["liquidity_score"] = (
            trading_value_score * 0.70
            +
            volume_score * 0.30
        )

        return df

    def calculate_momentum_score(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        당일 가격 움직임 기반 모멘텀 점수

        현재는 누적 데이터가 없으므로
        change_rate를 기반으로 계산한다.

        추후 데이터 누적 시
        다음 항목을 추가할 예정이다.

        - 단기 수익률
        - 이동평균
        - RSI
        - MACD
        - 거래량 증가율
        """

        df = market_df.copy()

        df["momentum_score"] = (
            self.normalize_series(
                df["change_rate"]
            )
        )

        return df

    def calculate_market_cap_score(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        기업 규모 점수 계산

        시가총액을 로그 변환하여
        지나치게 대형주에 점수가 몰리는 것을 완화한다.

        Parameters
        ----------
        market_df : pd.DataFrame

        Returns
        -------
        pd.DataFrame
        """

        df = market_df.copy()

        df["market_cap_score"] = (
            self.normalize_series(
                np.log1p(
                    df["market_cap"]
                )
            )
        )

        return df

    def calculate_total_score(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        최종 종합 점수 계산

        Score =
            유동성 점수
            +
            모멘텀 점수
            +
            시가총액 점수

        가중치는 ScreeningConfig에서 조정 가능하다.
        """

        df = market_df.copy()

        total_weight = (
            self.config.liquidity_weight
            +
            self.config.momentum_weight
            +
            self.config.market_cap_weight
        )

        if total_weight <= 0:
            raise ValueError(
                "Total screening weight "
                "must be greater than 0."
            )

        df["screening_score"] = (
            (
                df["liquidity_score"]
                * self.config.liquidity_weight
            )
            +
            (
                df["momentum_score"]
                * self.config.momentum_weight
            )
            +
            (
                df["market_cap_score"]
                * self.config.market_cap_weight
            )
        ) / total_weight

        return df

    def select_candidates(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        최종 후보 종목 선정

        종합 점수 기준으로 정렬하여
        상위 N개 종목을 반환한다.
        """

        df = market_df.copy()

        df = df.sort_values(
            by="screening_score",
            ascending=False
        )

        candidate_df = df.head(
            self.config.top_n
        ).copy()

        candidate_df.insert(
            0,
            "rank",
            range(
                1,
                len(candidate_df) + 1
            )
        )

        candidate_df = candidate_df.reset_index(
            drop=True
        )

        return candidate_df

    def run(
        self,
        market_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        전체 스크리닝 실행

        Parameters
        ----------
        market_df : pd.DataFrame
            MarketDataCollector가 수집한
            KOSPI + KOSDAQ 전체 시장 데이터

        Returns
        -------
        pd.DataFrame
            최종 후보 종목 DataFrame
        """

        logger.info(
            "=" * 50
        )

        logger.info(
            "Market screening started"
        )

        logger.info(
            f"Input stocks: {len(market_df)}"
        )

        # 1. 데이터 검증
        df = self.validate_market_data(
            market_df
        )

        # 2. 유동성 필터
        df = self.filter_liquidity(
            df
        )

        # 3. 시가총액 필터
        df = self.filter_market_cap(
            df
        )

        # 4. 극단적 가격 변동 제거
        df = self.filter_extreme_change(
            df
        )

        if df.empty:
            logger.warning(
                "No stocks passed the screening filters."
            )

            return pd.DataFrame()

        # 5. 유동성 점수
        df = self.calculate_liquidity_score(
            df
        )

        # 6. 모멘텀 점수
        df = self.calculate_momentum_score(
            df
        )

        # 7. 기업 규모 점수
        df = self.calculate_market_cap_score(
            df
        )

        # 8. 종합 점수
        df = self.calculate_total_score(
            df
        )

        # 9. 최종 후보군 선정
        candidates = self.select_candidates(
            df
        )

        logger.info(
            "Market screening completed"
        )

        logger.info(
            f"Final candidates: "
            f"{len(candidates)}"
        )

        logger.info(
            "=" * 50
        )

        return candidates