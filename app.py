"""
Simple client example for testing MCP Server locally.
This script simulates a client connecting to your MCP server.
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """Test the MCP server by simulating client requests."""
    print("Starting MCP server test client...")
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Prepare initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "client": "test-client",
            "version": "1.0.0",
            "protocols": ["mcp/0.1.0"]
        }
    }
    
    # Write initialization request to server
    server_process.stdin.write(json.dumps(init_request) + "\n")
    server_process.stdin.flush()
    
    # Read initialization response
    init_response = json.loads(await asyncio.to_thread(server_process.stdout.readline))
    print("Initialization response:", json.dumps(init_response, indent=2))
    
    # List tools request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "listTools",
        "params": {}
    }
    
    # Write list tools request to server
    server_process.stdin.write(json.dumps(list_tools_request) + "\n")
    server_process.stdin.flush()
    
    # Read list tools response
    list_tools_response = json.loads(await asyncio.to_thread(server_process.stdout.readline))
    print("\nAvailable tools:", json.dumps(list_tools_response, indent=2))
    
    # Test each tool
    tools = list_tools_response.get("result", {}).get("tools", [])
    
    for i, tool in enumerate(tools):
        tool_name = tool.get("name")
        print(f"\n\nTesting tool: {tool_name}")
        
        # Prepare test parameters based on tool name
        params = {}
        if tool_name == "search_code":
            params = {"query": "def", "directory": "."}
        elif tool_name == "analyze_dependencies":
            params = {"directory": "."}
        elif tool_name == "fetch_documentation":
            params = {"package": "httpx"}
        
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3 + i,
            "method": "callTool",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # Write call tool request to server
        server_process.stdin.write(json.dumps(call_tool_request) + "\n")
        server_process.stdin.flush()
        
        # Read call tool response
        call_tool_response = json.loads(await asyncio.to_thread(server_process.stdout.readline))
        print(f"\nResponse from {tool_name}:")
        
        # Extract the text content for better readability
        if "result" in call_tool_response and "content" in call_tool_response["result"]:
            for content in call_tool_response["result"]["content"]:
                if content["type"] == "text":
                    print("\n" + content["text"])
        else:
            print(json.dumps(call_tool_response, indent=2))
    
    # Shutdown request
    shutdown_request = {
        "jsonrpc": "2.0",
        "id": 99,
        "method": "shutdown",
        "params": {}
    }
    
    # Write shutdown request to server
    server_process.stdin.write(json.dumps(shutdown_request) + "\n")
    server_process.stdin.flush()
    
    # Read shutdown response
    shutdown_response = json.loads(await asyncio.to_thread(server_process.stdout.readline))
    print("\n\nShutdown response:", json.dumps(shutdown_response, indent=2))
    
    # Exit notification
    exit_notification = {
        "jsonrpc": "2.0",
        "method": "exit",
        "params": {}
    }
    
    # Write exit notification to server
    server_process.stdin.write(json.dumps(exit_notification) + "\n")
    server_process.stdin.flush()
    
    # Wait for server to exit
    await asyncio.to_thread(server_process.wait)
    print("\nServer exited")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
