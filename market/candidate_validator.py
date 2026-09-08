import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd


logger = logging.getLogger("CandidateValidator")


class CandidateValidator:
    """
    Screening Engine에서 생성된 후보 종목을 검증하는 클래스.

    역할:
    1. 필수 데이터 존재 여부 검증
    2. 가격 데이터 정상성 검증
    3. 거래량 검증
    4. 거래대금 최소 유동성 검증
    5. 시가총액 최소 기준 검증

    주의:
    이 클래스는 투자 추천 엔진이 아니다.
    Screening Engine의 후보 종목이 AI 분석에 전달 가능한
    정상적인 데이터인지 검증하는 역할을 담당한다.
    """

    REQUIRED_COLUMNS = [
        "ticker",
        "name",
        "market",
        "close",
        "volume",
        "trading_value",
        "market_cap",
    ]

    def __init__(
        self,
        min_volume: int = 1,
        min_trading_value: int = 1_000_000_000,
        min_market_cap: int = 100_000_000_000,
    ):
        """
        Parameters
        ----------
        min_volume : int
            최소 거래량

        min_trading_value : int
            최소 거래대금

        min_market_cap : int
            최소 시가총액
        """

        self.min_volume = min_volume
        self.min_trading_value = min_trading_value
        self.min_market_cap = min_market_cap

    def validate(
        self,
        candidates: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        후보 종목 전체를 검증한다.

        Parameters
        ----------
        candidates : pd.DataFrame
            Screening Engine에서 생성된 후보 종목

        Returns
        -------
        pd.DataFrame
            검증을 통과한 후보 종목
        """

        if candidates is None:
            logger.warning("Candidate data is None.")
            return pd.DataFrame()

        if candidates.empty:
            logger.warning("Candidate data is empty.")
            return candidates.copy()

        logger.info(
            f"Candidate validation started: "
            f"{len(candidates)} candidates"
        )

        validated_df = candidates.copy()

        # 1. 필수 컬럼 존재 여부 검증
        validated_df = self._validate_required_columns(
            validated_df
        )

        if validated_df.empty:
            logger.warning(
                "All candidates removed during "
                "required column validation."
            )
            return validated_df

        # 2. 결측치 검증
        validated_df = self._remove_missing_values(
            validated_df
        )

        if validated_df.empty:
            logger.warning(
                "All candidates removed during "
                "missing value validation."
            )
            return validated_df

        # 3. 가격 데이터 검증
        validated_df = self._validate_price_data(
            validated_df
        )

        if validated_df.empty:
            logger.warning(
                "All candidates removed during "
                "price validation."
            )
            return validated_df

        # 4. 거래량 검증
        validated_df = self._validate_volume(
            validated_df
        )

        if validated_df.empty:
            logger.warning(
                "All candidates removed during "
                "volume validation."
            )
            return validated_df

        # 5. 거래대금 검증
        validated_df = self._validate_trading_value(
            validated_df
        )

        if validated_df.empty:
            logger.warning(
                "All candidates removed during "
                "trading value validation."
            )
            return validated_df

        # 6. 시가총액 검증
        validated_df = self._validate_market_cap(
            validated_df
        )

        if validated_df.empty:
            logger.warning(
                "All candidates removed during "
                "market cap validation."
            )
            return validated_df

        logger.info(
            f"Candidate validation completed: "
            f"{len(validated_df)} candidates passed"
        )

        return validated_df.reset_index(drop=True)

    def _validate_required_columns(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        필수 컬럼 존재 여부 확인.
        """

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:

            logger.error(
                f"Missing required columns: "
                f"{missing_columns}"
            )

            return pd.DataFrame()

        return df

    def _remove_missing_values(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        필수 데이터의 결측치를 제거한다.
        """

        before_count = len(df)

        df = df.dropna(
            subset=self.REQUIRED_COLUMNS
        )

        removed_count = before_count - len(df)

        if removed_count > 0:

            logger.info(
                f"Missing value validation removed "
                f"{removed_count} candidates"
            )

        return df

    def _validate_price_data(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        가격 데이터 정상성 검증.

        검증 항목:
        - close > 0
        - open >= 0
        - high >= low
        - close가 high/low 범위 안에 존재
        """

        before_count = len(df)

        # close 가격은 반드시 존재
        condition = (
            df["close"] > 0
        )

        # open 컬럼이 있는 경우 검증
        if "open" in df.columns:

            condition &= (
                df["open"] >= 0
            )

        # high / low 컬럼이 있는 경우 검증
        if (
            "high" in df.columns
            and "low" in df.columns
        ):

            condition &= (
                df["high"] >= df["low"]
            )

            condition &= (
                df["close"] <= df["high"]
            )

            condition &= (
                df["close"] >= df["low"]
            )

        df = df[condition]

        removed_count = before_count - len(df)

        if removed_count > 0:

            logger.info(
                f"Price validation removed "
                f"{removed_count} candidates"
            )

        return df

    def _validate_volume(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        최소 거래량 검증.
        """

        before_count = len(df)

        df = df[
            df["volume"] >= self.min_volume
        ]

        removed_count = before_count - len(df)

        if removed_count > 0:

            logger.info(
                f"Volume validation removed "
                f"{removed_count} candidates"
            )

        return df

    def _validate_trading_value(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        최소 거래대금 검증.
        """

        before_count = len(df)

        df = df[
            df["trading_value"]
            >= self.min_trading_value
        ]

        removed_count = before_count - len(df)

        if removed_count > 0:

            logger.info(
                f"Trading value validation removed "
                f"{removed_count} candidates"
            )

        return df

    def _validate_market_cap(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        최소 시가총액 검증.
        """

        before_count = len(df)

        df = df[
            df["market_cap"]
            >= self.min_market_cap
        ]

        removed_count = before_count - len(df)

        if removed_count > 0:

            logger.info(
                f"Market cap validation removed "
                f"{removed_count} candidates"
            )

        return df

    def validate_single_candidate(
        self,
        candidate: Dict,
    ) -> Tuple[bool, List[str]]:
        """
        단일 후보 종목 검증.

        Parameters
        ----------
        candidate : Dict
            단일 후보 종목 데이터

        Returns
        -------
        Tuple[bool, List[str]]

        bool
            검증 통과 여부

        List[str]
            검증 실패 사유
        """

        errors = []

        # 필수 필드 검증
        for column in self.REQUIRED_COLUMNS:

            if column not in candidate:

                errors.append(
                    f"Missing required field: {column}"
                )

                continue

            if candidate[column] is None:

                errors.append(
                    f"Null value: {column}"
                )

        # 필수 데이터가 없으면 이후 검증 불필요
        if errors:
            return False, errors

        # 가격 검증
        close = candidate.get("close")

        if close <= 0:

            errors.append(
                "Invalid close price"
            )

        # 거래량 검증
        volume = candidate.get("volume")

        if volume < self.min_volume:

            errors.append(
                f"Volume below minimum: "
                f"{volume}"
            )

        # 거래대금 검증
        trading_value = candidate.get(
            "trading_value"
        )

        if trading_value < self.min_trading_value:

            errors.append(
                f"Trading value below minimum: "
                f"{trading_value}"
            )

        # 시가총액 검증
        market_cap = candidate.get(
            "market_cap"
        )

        if market_cap < self.min_market_cap:

            errors.append(
                f"Market cap below minimum: "
                f"{market_cap}"
            )

        # high / low 검증
        high = candidate.get("high")
        low = candidate.get("low")

        if high is not None and low is not None:

            if high < low:

                errors.append(
                    "High price is lower than low price"
                )

            if close > high:

                errors.append(
                    "Close price is above high price"
                )

            if close < low:

                errors.append(
                    "Close price is below low price"
                )

        return len(errors) == 0, errors