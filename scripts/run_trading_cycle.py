import sys
import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# Project Path Configuration
# ============================================================

# run_trading_cycle.py
#   -> scripts/
#   -> 프로젝트 루트 C:\AI_Trading_Agent

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 프로젝트 루트를 Python import 경로 최우선으로 등록
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Environment Configuration
# ============================================================

ENV_FILE = PROJECT_ROOT / ".env"

if not ENV_FILE.exists():
    print(f"[ERROR] .env 파일을 찾을 수 없습니다: {ENV_FILE}")
    sys.exit(1)

# 프로젝트 루트의 .env를 명시적으로 로드
#
# override=True:
# 외부 환경변수에 동일한 이름이 존재하더라도
# 프로젝트의 .env 값을 우선 사용한다.
load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ============================================================
# Runtime Imports
# ============================================================

from runtime.executor.main import RuntimeExecutor
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.detailed_report_generator import (
    DetailedReportGenerator
)
from runtime.tool_manager.research_report_generator import (
    ResearchReportGenerator
)


# ============================================================
# Environment Helpers
# ============================================================

def get_env_bool(name: str, default: bool = False) -> bool:
    """
    환경변수를 Boolean으로 변환한다.

    True:
        true / 1 / yes / y / on

    False:
        false / 0 / no / n / off
    """

    value = os.environ.get(name)

    if value is None:
        return default

    value = value.strip().lower()

    if value in ("true", "1", "yes", "y", "on"):
        return True

    if value in ("false", "0", "no", "n", "off"):
        return False

    print(
        f"[WARNING] {name} 값이 올바르지 않습니다: "
        f"'{value}' -> 기본값 {default} 사용"
    )

    return default


def validate_api_key(name: str) -> bool:
    """
    환경변수에 API Key가 정상적으로 존재하는지 확인한다.

    실제 API Key 값은 출력하지 않는다.
    """

    value = os.environ.get(name)

    if not value:
        return False

    value = value.strip()

    # 잘못된 환경변수 파싱으로 "=" 자체가 들어오는 경우 방지
    if value == "=":
        return False

    return True


# ============================================================
# Trading Mode Detection
# ============================================================

def detect_trading_mode(
    use_mock_ai: bool,
    use_mock_claude: bool
) -> str:
    """
    USE_MOCK_AI / USE_MOCK_CLAUDE 조합으로
    Trading Mode를 자동 결정한다.

    ------------------------------------------------------------
    USE_MOCK_AI   USE_MOCK_CLAUDE   MODE
    ------------------------------------------------------------
    true          true              MOCK
    false         true              SINGLE (GPT)
    true          false             SINGLE (CLAUDE)
    false         false             MULTI
    ------------------------------------------------------------
    """

    if use_mock_ai and use_mock_claude:
        return "MOCK"

    if not use_mock_ai and use_mock_claude:
        return "SINGLE (GPT)"

    if use_mock_ai and not use_mock_claude:
        return "SINGLE (CLAUDE)"

    return "MULTI"


# ============================================================
# Main Trading Cycle
# ============================================================

async def main():

    # --------------------------------------------------------
    # Environment Values
    # --------------------------------------------------------

    use_mock_ai = get_env_bool(
        "USE_MOCK_AI",
        default=True
    )

    use_mock_claude = get_env_bool(
        "USE_MOCK_CLAUDE",
        default=True
    )


    # --------------------------------------------------------
    # Detect Trading Mode
    # --------------------------------------------------------

    display_mode = detect_trading_mode(
        use_mock_ai,
        use_mock_claude
    )


    # ========================================================
    # Startup Information
    # ========================================================

    print("========================================")
    print(" AI Trading Agent")
    print("========================================")
    print(f" Project Root : {PROJECT_ROOT}")
    print(f" .env         : {ENV_FILE}")
    print(f" Trading Mode : {display_mode}")
    print(" Database     : data/trading.db")
    print("========================================")


    # ========================================================
    # Environment Debug Information
    # ========================================================

    # API Key 실제 값은 절대 출력하지 않는다.
    # 존재 여부와 길이만 확인한다.

    print("----------------------------------------")

    print(
        f" USE_MOCK_AI     : "
        f"{os.environ.get('USE_MOCK_AI', '<not set>')}"
    )

    print(
        f" USE_MOCK_CLAUDE : "
        f"{os.environ.get('USE_MOCK_CLAUDE', '<not set>')}"
    )

    print(
        f" OPENAI_API_KEY  : "
        f"{'LOADED' if validate_api_key('OPENAI_API_KEY') else 'NOT LOADED'}"
    )

    print(
        f" ANTHROPIC_API_KEY: "
        f"{'LOADED' if validate_api_key('ANTHROPIC_API_KEY') else 'NOT LOADED'}"
    )

    claude_model = os.environ.get(
        "CLAUDE_MODEL",
        "<not set>"
    )

    print(
        f" CLAUDE_MODEL    : "
        f"{claude_model}"
    )

    print("----------------------------------------")


    # ========================================================
    # API Key Validation
    # ========================================================

    # --------------------------------------------------------
    # GPT 실제 사용
    # --------------------------------------------------------

    if not use_mock_ai:

        if not validate_api_key("OPENAI_API_KEY"):
            print(
                "[ERROR] GPT 실제 API 사용을 위해 "
                "OPENAI_API_KEY가 필요합니다."
            )
            sys.exit(1)

        print("[OK] OPENAI_API_KEY 로드 확인")


    # --------------------------------------------------------
    # Claude 실제 사용
    # --------------------------------------------------------

    if not use_mock_claude:

        if not validate_api_key("ANTHROPIC_API_KEY"):
            print(
                "[ERROR] Claude 실제 API 사용을 위해 "
                "ANTHROPIC_API_KEY가 필요합니다."
            )
            sys.exit(1)

        print("[OK] ANTHROPIC_API_KEY 로드 확인")


    # ========================================================
    # Execute Trading Cycle
    # ========================================================

    try:

        executor = RuntimeExecutor(
            db_path=str(
                PROJECT_ROOT / "data" / "trading.db"
            )
        )

        await executor.run_cycle()

        print("[OK] Trading Agent 실행 완료")

    except Exception as e:

        print(
            f"[ERROR] Trading Agent 실행에 실패했습니다: {e}"
        )

        sys.exit(1)


    # ========================================================
    # Generate Reports
    # ========================================================

    try:

        db = DatabaseManager(
            db_path=str(
                PROJECT_ROOT / "data" / "trading.db"
            )
        )


        # ----------------------------------------------------
        # Detailed Trading Report
        # ----------------------------------------------------

        detailed_gen = DetailedReportGenerator(db)

        detailed_gen.generate_report()

        print("[OK] 상세 거래 보고서 생성 완료")


        # ----------------------------------------------------
        # AI Research Report
        # ----------------------------------------------------

        research_gen = ResearchReportGenerator(db)

        research_gen.generate_report()

        print("[OK] AI 연구 보고서 생성 완료")


    except Exception as e:

        print(
            f"[ERROR] 보고서 생성 실패: {e}"
        )

        sys.exit(1)


    # ========================================================
    # Completed
    # ========================================================

    print("========================================")
    print(" Trading Cycle Completed")
    print("========================================")
    print("이제 프로그램 결과와 보고서를 확인하세요.")
    print("========================================")


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())