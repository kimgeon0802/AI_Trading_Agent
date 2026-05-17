import asyncio
import os
from runtime.executor.main import RuntimeExecutor

async def test_simulated_market():
    os.environ["USE_MOCK_AI"] = "true"
    executor = RuntimeExecutor()
    
    print("--- Cycle 1: Bullish ---")
    await executor.run_cycle('bullish')
    
    print("\n--- Cycle 2: Bullish ---")
    await executor.run_cycle('bullish')
    
    print("\n--- Cycle 3: Bearish ---")
    await executor.run_cycle('bearish')
    
    print("\n--- Cycle 4: Bearish ---")
    await executor.run_cycle('bearish')

if __name__ == "__main__":
    asyncio.run(test_simulated_market())
