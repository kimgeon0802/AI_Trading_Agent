import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="data/trading.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ticker TEXT,
                    decision TEXT,
                    quantity INTEGER,
                    price REAL,
                    confidence REAL
                )
            ''')
            
            # predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ticker TEXT,
                    prediction TEXT,
                    expected_return REAL,
                    confidence REAL,
                    reasoning TEXT
                )
            ''')
            
            # reasoning_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reasoning_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    decision TEXT,
                    reasoning TEXT,
                    risks TEXT,
                    confidence REAL
                )
            ''')
            
            # evaluation_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    prediction_id INTEGER,
                    actual_result TEXT,
                    evaluation TEXT,
                    success BOOLEAN
                )
            ''')
            
            # market_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    market_data TEXT
                )
            ''')
            
            # portfolio table (added for Phase 1)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cash REAL,
                    total_asset REAL,
                    timestamp TEXT
                )
            ''')
            
            # holdings table (added for Phase 1)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    quantity INTEGER,
                    average_price REAL
                )
            ''')
            
            conn.commit()

    def execute_query(self, query, params=()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()

    def save_reasoning(self, decision, reasoning, risks, confidence, timestamp):
        query = "INSERT INTO reasoning_logs (timestamp, decision, reasoning, risks, confidence) VALUES (?, ?, ?, ?, ?)"
        self.execute_query(query, (timestamp, decision, str(reasoning), str(risks), confidence))

    def save_prediction(self, ticker, prediction, expected_return, confidence, reasoning, timestamp):
        query = "INSERT INTO predictions (timestamp, ticker, prediction, expected_return, confidence, reasoning) VALUES (?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (timestamp, ticker, prediction, expected_return, confidence, reasoning))

    def get_portfolio(self):
        query = "SELECT cash, total_asset FROM portfolio ORDER BY id DESC LIMIT 1"
        result = self.execute_query(query)
        if result:
            return {"cash": result[0][0], "total_asset": result[0][1]}
        return None

    def update_portfolio(self, cash, total_asset, timestamp):
        query = "INSERT INTO portfolio (cash, total_asset, timestamp) VALUES (?, ?, ?)"
        self.execute_query(query, (cash, total_asset, timestamp))

    def get_holdings(self):
        query = "SELECT ticker, quantity, average_price FROM holdings WHERE quantity > 0"
        results = self.execute_query(query)
        return [{"ticker": r[0], "quantity": r[1], "average_price": r[2]} for r in results]

    def update_holding(self, ticker, quantity, average_price):
        # Check if holding exists
        query = "SELECT id FROM holdings WHERE ticker = ?"
        result = self.execute_query(query, (ticker,))
        if result:
            if quantity > 0:
                update_query = "UPDATE holdings SET quantity = ?, average_price = ? WHERE ticker = ?"
                self.execute_query(update_query, (quantity, average_price, ticker))
            else:
                delete_query = "DELETE FROM holdings WHERE ticker = ?"
                self.execute_query(delete_query, (ticker,))
        elif quantity > 0:
            insert_query = "INSERT INTO holdings (ticker, quantity, average_price) VALUES (?, ?, ?)"
            self.execute_query(insert_query, (ticker, quantity, average_price))

    def save_trade(self, timestamp, ticker, decision, quantity, price, confidence):
        query = "INSERT INTO trades (timestamp, ticker, decision, quantity, price, confidence) VALUES (?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (timestamp, ticker, decision, quantity, price, confidence))
