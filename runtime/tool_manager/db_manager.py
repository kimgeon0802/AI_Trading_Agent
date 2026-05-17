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
