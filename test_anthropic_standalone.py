import anthropic
import os
from dotenv import load_dotenv

# Load env from the same directory where main.py exists
load_dotenv(dotenv_path="C:/AI_Trading_Agent/.env")

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key found: {bool(api_key)}")

client = anthropic.Anthropic(api_key=api_key)

try:
    print("Testing claude-3-5-sonnet-20241022...")
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "hi"}]
    )
    print("Success")
except anthropic.BadRequestError as e:
    print(f"BadRequestError: {e}")
except anthropic.APIConnectionError as e:
    print(f"APIConnectionError: {e}")
except Exception as e:
    print(f"Exception: {type(e).__name__} - {e}")
