import pytest
import os
from pathlib import Path
from account.account_manager import AccountManager
from runtime.tool_manager.db_manager import DatabaseManager

class MockDB(DatabaseManager):
    def __init__(self):
        self.portfolio = {"cash": 0, "total_asset": 0}
        self.holdings = []
    def get_portfolio(self): return self.portfolio
    def update_portfolio(self, cash, total_asset, timestamp): 
        self.portfolio = {"cash": cash, "total_asset": total_asset}

@pytest.fixture
def account_manager(tmp_path):
    cash_file = tmp_path / "cash.txt"
    cash_file.write_text("10000000")
    db = MockDB()
    return AccountManager(db, str(cash_file)), cash_file

def test_deposit(account_manager):
    am, _ = account_manager
    am.deposit(5000000)
    
    balances = am.get_balances()
    assert balances["external_cash"] == 5000000
    assert balances["virtual_cash"] == 5000000

def test_withdraw(account_manager):
    am, _ = account_manager
    am.deposit(5000000)
    am.withdraw(2000000)
    
    balances = am.get_balances()
    assert balances["external_cash"] == 7000000
    assert balances["virtual_cash"] == 3000000

def test_invalid_cash_file(tmp_path):
    cash_file = tmp_path / "cash.txt"
    cash_file.write_text("1,000,000") # Invalid comma
    db = MockDB()
    with pytest.raises(ValueError, match="숫자"):
        AccountManager(db, str(cash_file))
