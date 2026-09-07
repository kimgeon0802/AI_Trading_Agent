import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="data/trading.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.connection.cursor()
        
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
        # Check if prediction_id exists in trades, if not, add it
        cursor.execute("PRAGMA table_info(trades)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'prediction_id' not in columns:
            cursor.execute('ALTER TABLE trades ADD COLUMN prediction_id INTEGER')
            self.connection.commit()
        
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
                prediction_id INTEGER,
                timestamp TEXT,
                decision TEXT,
                reasoning TEXT,
                risks TEXT,
                confidence REAL
            )
        ''')
        # Ensure prediction_id exists in reasoning_logs if table already existed without it
        cursor.execute("PRAGMA table_info(reasoning_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'prediction_id' not in columns:
            cursor.execute('ALTER TABLE reasoning_logs ADD COLUMN prediction_id INTEGER')
            self.connection.commit()
        
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
        
        # macro_indicators table (added for Phase 2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macro_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                indicator_name TEXT,
                value REAL
            )
        ''')
        
        # agent_decisions table (added for Phase 3)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                timestamp TEXT,
                model_name TEXT,
                decision TEXT,
                confidence REAL,
                reasoning TEXT,
                risk_assessment TEXT
            )
        ''')
        
        self.connection.commit()

    def execute_query(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.fetchall()

    def save_macro_data(self, indicator_name, value, timestamp):
        # Prune old data for this indicator before inserting new
        self.execute_query("DELETE FROM macro_indicators WHERE indicator_name = ?", (indicator_name,))
        query = "INSERT INTO macro_indicators (timestamp, indicator_name, value) VALUES (?, ?, ?)"
        self.execute_query(query, (timestamp, indicator_name, value))

    def get_latest_macro_data(self):
        query = """
            SELECT indicator_name, value 
            FROM macro_indicators 
            WHERE id IN (
                SELECT MAX(id) 
                FROM macro_indicators 
                GROUP BY indicator_name
            )
        """
        results = self.execute_query(query)
        return {r[0]: r[1] for r in results}

    def save_reasoning(self, decision, reasoning, risks, confidence, timestamp, prediction_id=None):
        query = "INSERT INTO reasoning_logs (timestamp, decision, reasoning, risks, confidence, prediction_id) VALUES (?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (timestamp, decision, str(reasoning), str(risks), confidence, prediction_id))

    def save_prediction(self, ticker, prediction, expected_return, confidence, reasoning, timestamp):
        query = "INSERT INTO predictions (timestamp, ticker, prediction, expected_return, confidence, reasoning) VALUES (?, ?, ?, ?, ?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(query, (timestamp, ticker, prediction, expected_return, confidence, reasoning))
        self.connection.commit()
        return cursor.lastrowid

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

    def save_trade(self, timestamp, ticker, decision, quantity, price, confidence, prediction_id=None):
        query = "INSERT INTO trades (timestamp, ticker, decision, quantity, price, confidence, prediction_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (timestamp, ticker, decision, quantity, price, confidence, prediction_id))

    def get_pending_evaluations(self):
        # Get predictions that haven't been evaluated yet
        query = """
            SELECT p.id, p.timestamp, p.ticker, p.prediction, p.confidence 
            FROM predictions p
            LEFT JOIN evaluation_logs e ON p.id = e.prediction_id
            WHERE e.id IS NULL
        """
        results = self.execute_query(query)
        return [{"id": r[0], "timestamp": r[1], "ticker": r[2], "prediction": r[3], "confidence": r[4]} for r in results]

    def save_agent_decision(self, prediction_id, timestamp, model_name, decision, confidence, reasoning, risk_assessment):
        query = "INSERT INTO agent_decisions (prediction_id, timestamp, model_name, decision, confidence, reasoning, risk_assessment) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (prediction_id, timestamp, model_name, decision, confidence, str(reasoning), str(risk_assessment)))

    def save_evaluation(self, prediction_id, actual_result, evaluation, success, timestamp):
        query = "INSERT INTO evaluation_logs (timestamp, prediction_id, actual_result, evaluation, success) VALUES (?, ?, ?, ?, ?)"
        self.execute_query(query, (timestamp, prediction_id, actual_result, evaluation, success))

    def get_evaluation_summaries(self):
        query = """
            SELECT e.timestamp, p.ticker, p.prediction, e.actual_result, e.evaluation, e.success
            FROM evaluation_logs e
            JOIN predictions p ON e.prediction_id = p.id
            ORDER BY e.timestamp DESC
        """
        results = self.execute_query(query)
        return [{"timestamp": r[0], "ticker": r[1], "prediction": r[2], "result": r[3], "evaluation": r[4], "success": r[5]} for r in results]
