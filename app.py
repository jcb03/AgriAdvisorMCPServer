import os
from dotenv import load_dotenv
import requests
import time
import threading
import signal
import sys

# Load environment variables FIRST
load_dotenv()

# Test if loading worked
api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"✅ API Key starts with: {api_key[:10]}...")

import uvicorn
from mcp_server import mcp

# Get the pure MCP app
app = mcp.http_app()

# 🏥 ADD HEALTH ENDPOINT
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agriculture-mcp", "timestamp": time.time()}

# 🔄 IMPROVED KEEP-ALIVE FUNCTION
def keep_server_alive():
    """Enhanced keep-alive function with better error handling"""
    base_url = "https://agriadvisormcp.onrender.com"
    
    def ping_server():
        consecutive_failures = 0
        max_failures = 3
        
        while True:
            try:
                time.sleep(600)  # 10 minutes (safer interval)
                
                # Try multiple endpoints
                endpoints = ["/health", "/", ""]
                success = False
                
                for endpoint in endpoints:
                    try:
                        url = f"{base_url}{endpoint}".rstrip('/')
                        response = requests.get(url, timeout=30)
                        
                        if response.status_code in [200, 202]:
                            print(f"🔄 Keep-alive SUCCESS: {response.status_code} - {url}")
                            consecutive_failures = 0
                            success = True
                            break
                        else:
                            print(f"⚠️ Keep-alive WARNING: {response.status_code} - {url}")
                            
                    except requests.exceptions.RequestException as e:
                        print(f"⚠️ Keep-alive ERROR for {endpoint}: {str(e)}")
                        continue
                
                if not success:
                    consecutive_failures += 1
                    print(f"❌ Keep-alive FAILED (attempt {consecutive_failures}/{max_failures})")
                    
                    if consecutive_failures >= max_failures:
                        print("🚨 Multiple keep-alive failures - server may be down")
                        consecutive_failures = 0  # Reset counter
                        
            except Exception as e:
                print(f"❌ Keep-alive EXCEPTION: {str(e)}")
                time.sleep(60)  # Wait before retrying on exception
    
    # Start daemon thread
    thread = threading.Thread(target=ping_server, daemon=True, name="KeepAliveThread")
    thread.start()
    print("🔄 Enhanced keep-alive service started (10-min interval)")
    return thread

# 🛡️ GRACEFUL SHUTDOWN HANDLER
def signal_handler(sig, frame):
    print(f"\n🛑 Received {signal.Signals(sig).name} - Shutting down gracefully...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Start keep-alive service
    keep_alive_thread = keep_server_alive()
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
