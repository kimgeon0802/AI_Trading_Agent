import asyncio
import os
import random
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from runtime.executor.main import RuntimeExecutor

# Set Mock Mode
os.environ["USE_MOCK_AI"] = "true"
os.environ["USE_MOCK_CLAUDE"] = "true"
os.environ["TRADING_AI_MODE"] = "multi"

async def generate_data(num_cycles=50):
    # Use a test database
    os.environ["DB_PATH"] = "data/test_trading.db"
    
    # Initialize executor (this will use the test DB)
    # Need to override DB_PATH in DatabaseManager if it reads from environment
    # or just make sure it uses the path provided to it.
    
    # The RuntimeExecutor initializes DatabaseManager without arguments
    # Let's modify DB_PATH environment variable before initializing DatabaseManager
    os.environ["DB_PATH"] = "data/test_trading.db"
    
    executor = RuntimeExecutor()
    
    # Create test DB if doesn't exist
    if os.path.exists("data/test_trading.db"):
        os.remove("data/test_trading.db")
        
    # Re-initialize executor to ensure it uses the test DB
    executor = RuntimeExecutor(db_path="data/test_trading.db")

    print(f"Generating {num_cycles} cycles of mock data...")
    
    for i in range(num_cycles):
        print(f"Cycle {i+1}/{num_cycles}")
        # Random condition for variety
        condition = random.choice(["bull", "bear", "neutral"])
        await executor.run_cycle(market_condition=condition)

    print("Data generation complete.")

if __name__ == "__main__":
    asyncio.run(generate_data(num_cycles=50))
