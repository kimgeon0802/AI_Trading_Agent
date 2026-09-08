from market.market_data_collector import MarketDataCollector
from market.screening_engine import ScreeningEngine
from market.candidate_validator import CandidateValidator


def main():

    print("=" * 60)
    print(" MARKET SCREENING PIPELINE TEST")
    print("=" * 60)

    # 1. 전체 시장 데이터 수집
    collector = MarketDataCollector()

    market_df = collector.collect_all_markets()

    print()
    print(f"[INFO] 전체 시장 데이터: {len(market_df)}개")

    # 2. 1차 스크리닝
    screening_engine = ScreeningEngine()

    candidates_df = screening_engine.run(market_df)

    print()
    print(f"[INFO] 스크리닝 후보군: {len(candidates_df)}개")

    # 3. 후보 검증
    validator = CandidateValidator()

    validated_df = validator.validate(candidates_df)

    print()
    print(f"[INFO] 최종 검증 후보군: {len(validated_df)}개")

    print()
    print("=" * 60)
    print(" FINAL CANDIDATES")
    print("=" * 60)

    if validated_df.empty:

        print("[WARNING] 최종 후보가 없습니다.")

    else:

        display_columns = [
            "ticker",
            "name",
            "market",
            "close",
            "change_rate",
            "volume",
            "market_cap"
        ]

        available_columns = [
            col
            for col in display_columns
            if col in validated_df.columns
        ]

        print(
            validated_df[available_columns]
            .head(20)
            .to_string(index=False)
        )

    print()
    print("=" * 60)
    print(" PIPELINE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()