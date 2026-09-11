import os
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from runtime.tool_manager.db_manager import DatabaseManager

logger = logging.getLogger("AccountManager")

class AccountManager:
    """
    외부 cash.txt 파일(실제 보유 현금)과
    시스템 내부 가상 증권계좌(PortfolioManager/DB) 간의 자금 이동 관리.
    """
    
    def __init__(self, db_manager: DatabaseManager, cash_file: str = "cash.txt"):
        self.db = db_manager
        self.cash_file = Path(cash_file)
        self._validate_file_exists()
        self._get_cash_from_file() # Ensure content is valid on init

    def _validate_file_exists(self):
        if not self.cash_file.exists():
            raise FileNotFoundError(
                f"사용자의 현금 보유량을 나타내는 {self.cash_file} 파일이 존재하지 않습니다. "
                "정상적인 사용을 위해 해당 파일을 생성하고 보유 현금을 입력하세요."
            )

    def _get_cash_from_file(self) -> int:
        content = self.cash_file.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("cash.txt 파일이 비어 있습니다.")
        if not re.match(r"^\d+$", content):
            raise ValueError("cash.txt 파일은 오직 숫자(정수)만 포함해야 합니다.")
        return int(content)

    def _save_cash_to_file(self, amount: int):
        self.cash_file.write_text(str(amount), encoding="utf-8")

    def get_balances(self) -> Dict[str, int]:
        """
        현재 외부 현금(cash.txt)과 가상계좌 현금(DB)을 조회.
        """
        external_cash = self._get_cash_from_file()
        portfolio = self.db.get_portfolio()
        virtual_cash = portfolio["cash"] if portfolio else 0
        
        return {
            "external_cash": external_cash,
            "virtual_cash": int(virtual_cash)
        }

    def deposit(self, amount: int) -> bool:
        """
        외부 현금 -> 가상계좌 입금
        """
        if amount <= 0:
            raise ValueError("입금액은 0보다 커야 합니다.")

        external_cash = self._get_cash_from_file()
        if amount > external_cash:
            raise ValueError(f"입금 불가능: 보유 외부 현금({external_cash})보다 입금액({amount})이 큽니다.")
            
        # 가상계좌 상태 읽기
        portfolio = self.db.get_portfolio()
        if not portfolio:
            virtual_cash = 0
            total_asset = amount
        else:
            virtual_cash = portfolio["cash"]
            total_asset = portfolio["total_asset"] + amount
            
        # Atomic 처리
        # 1. 계산
        new_external_cash = external_cash - amount
        new_virtual_cash = virtual_cash + amount
        
        # 2. 저장 (파일 -> DB)
        self._save_cash_to_file(new_external_cash)
        self.db.update_portfolio(new_virtual_cash, total_asset, datetime.now().isoformat())
        
        logger.info(f"Deposit SUCCESS: {amount} KRW")
        return True

    def withdraw(self, amount: int) -> bool:
        """
        가상계좌 현금 -> 외부 현금 출금
        """
        if amount <= 0:
            raise ValueError("출금액은 0보다 커야 합니다.")

        portfolio = self.db.get_portfolio()
        virtual_cash = portfolio["cash"] if portfolio else 0
        
        if amount > virtual_cash:
            raise ValueError(f"출금 불가능: 가상계좌 현금({virtual_cash})보다 출금액({amount})이 큽니다.")
            
        external_cash = self._get_cash_from_file()
        
        # Atomic 처리
        new_virtual_cash = virtual_cash - amount
        new_total_asset = portfolio["total_asset"] - amount
        new_external_cash = external_cash + amount
        
        self.db.update_portfolio(new_virtual_cash, new_total_asset, datetime.now().isoformat())
        self._save_cash_to_file(new_external_cash)
        
        logger.info(f"Withdraw SUCCESS: {amount} KRW")
        return True
