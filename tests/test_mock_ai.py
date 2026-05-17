import os
import asyncio
from runtime.executor.main import RuntimeExecutor

async def test_mock_run():
    # Force USE_MOCK_AI for this test
    os.environ["USE_MOCK_AI"] = "true"
    
    executor = RuntimeExecutor()
    print("Starting Mock AI test run...")
    await executor.run_cycle()
    print("Mock AI test run completed.")

if __name__ == "__main__":
    asyncio.run(test_mock_run())
