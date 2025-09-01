import requests
import json

BASE_URL = "http://localhost:8000"
BEARER_TOKEN = "puch2024"

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

def check_mcp_server():
    """Check MCP server using proper JSON-RPC protocol"""
    print("🔍 Checking MCP Server...")
    
    # Test server response
    try:
        response = requests.post(BASE_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }, timeout=10)
        
        print(f"Server Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tools = data.get("result", {}).get("tools", [])
            print(f"✅ MCP Server Working! Found {len(tools)} tools:")
            
            for i, tool in enumerate(tools, 1):
                tool_name = tool.get("name", "unnamed")
                description = tool.get("description", "No description")
                print(f"   {i}. 🔧 {tool_name}")
                print(f"      📝 {description[:80]}...")
            
            return tools
        else:
            print(f"❌ Server Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return []

def test_simple_tool():
    """Test a simple diagnostic tool"""
    print("\n🧪 Testing Simple Tool...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "health_check",
            "arguments": {}
        },
        "id": 1
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Tool execution working!")
            data = response.json()
            print(f"📊 Response structure: {list(data.keys())}")
        else:
            print(f"❌ Tool Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🔍 MCP Server Diagnostic Check")
    print("=" * 40)
    
    tools = check_mcp_server()
    if tools:
        test_simple_tool()
    else:
        print("❌ Cannot test tools - server not responding")
    
    print("\n💡 Note: 404 errors on /tools, /docs etc. are NORMAL for FastMCP servers!")
    print("✅ FastMCP uses JSON-RPC protocol, not REST endpoints")
