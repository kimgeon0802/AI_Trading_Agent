import sys
from pathlib import Path

# Setup path immediately
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import os
from runtime.tool_manager.db_manager import DatabaseManager
from account.account_manager import AccountManager

def main():
    db = DatabaseManager()
    am = AccountManager(db, cash_file="cash.txt")
    
    while True:
        balances = am.get_balances()
        print("\n========================================")
        print(" AI Trading Agent - Account Manager")
        print("========================================")
        print(f"\n[Actual Account]")
        print(f"Cash.txt Balance : {balances['external_cash']:,} KRW")
        print(f"\n[Virtual Securities Account]")
        # Portfolio values from DB
        portfolio = db.get_portfolio()
        holdings = db.get_holdings()
        val = sum(h["quantity"] * h["average_price"] for h in holdings) # Simplification
        print(f"Available Cash   : {balances['virtual_cash']:,} KRW")
        print(f"Holdings Value   : {val:,} KRW")
        print(f"Total Value      : {(balances['virtual_cash'] + val):,} KRW")
        print("\n----------------------------------------")
        print("1. Balance\n2. Deposit\n3. Withdraw\n0. Exit")
        
        choice = input("\nSelect: ")
        
        if choice == '1': continue
        elif choice == '2':
            amount = int(input("Deposit Amount: "))
            if input(f"Proceed? [y/N]: ").lower() == 'y':
                am.deposit(amount)
        elif choice == '3':
            amount = int(input("Withdraw Amount: "))
            if input(f"Proceed? [y/N]: ").lower() == 'y':
                am.withdraw(amount)
        elif choice == '0':
            break

if __name__ == "__main__":
    main()
