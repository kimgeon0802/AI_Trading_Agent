import asyncio
import os
from runtime.executor.main import RuntimeExecutor

def test_simulated_market():
    os.environ["USE_MOCK_AI"] = "true"
    executor = RuntimeExecutor()
    
    async def run_cycles():
        print("--- Cycle 1: Bullish ---")
        await executor.run_cycle('bullish')
        
        print("\n--- Cycle 2: Bullish ---")
        await executor.run_cycle('bullish')
        
        print("\n--- Cycle 3: Bearish ---")
        await executor.run_cycle('bearish')
        
        print("\n--- Cycle 4: Bearish ---")
        await executor.run_cycle('bearish')

    asyncio.run(run_cycles())

if __name__ == "__main__":
    test_simulated_market()
