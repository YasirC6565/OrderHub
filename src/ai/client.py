import os
from openai import OpenAI

# Initialize client only if API key is available
# This allows the app to start even if OpenAI isn't configured
_api_key = os.getenv("OPENAI_API_KEY")
if _api_key:
    client = OpenAI(api_key=_api_key)
else:
    client = None
    print("⚠️  Warning: OPENAI_API_KEY not set. AI features will be disabled.")
