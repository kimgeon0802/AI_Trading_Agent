import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
try:
    # Anthropic doesn't have a simple list_models endpoint in the basic client, 
    # but I can try to use a known model and if it fails, I'll know if the key works.
    # Actually, let's try claude-3-5-sonnet-20241022 as it is a standard model.
    print("Testing claude-3-5-sonnet-20241022")
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "hi"}]
    )
    print("Success")
except Exception as e:
    print(f"Error: {e}")
