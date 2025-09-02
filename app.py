import os
from dotenv import load_dotenv
import requests
import time
import threading

# Load environment variables FIRST
load_dotenv()

# Test if loading worked
api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"✅ API Key starts with: {api_key[:10]}...")

import uvicorn
from mcp_server import mcp

# Get the pure MCP app - NO FASTAPI
app = mcp.http_app()

# KEEP-ALIVE FUNCTION
def keep_server_alive():
    """Simple keep-alive function"""
    url = "https://agriadvisormcp.onrender.com"  # Your actual URL
    
    def ping_server():
        while True:
            try:
                time.sleep(720)  # 14 minutes
                response = requests.get(f"{url}", timeout=30)
                print(f"🔄 Keep-alive: {response.status_code}")
            except:
                print("⚠️ Keep-alive ping failed")
    
    # Start in background thread
    thread = threading.Thread(target=ping_server, daemon=True)
    thread.start()
    print("🔄 Keep-alive service started")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        access_log=True
    )
