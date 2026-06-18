import os
import sys
import asyncio
from fastmcp import Client

async def test_hybrid_server():
    """
    Connects to the server_template.py programmatically using FastMCP Client,
    lists discovered tools, and executes a tool call.
    """
    print("==================================================")
    print("   TESTING HYBRID SERVER TEMPLATE TOOL INTEGRATION ")
    print("==================================================")
    
    # Run server_template.py in stdio mode as a subprocess and connect to it
    async with Client("server_template.py") as client:
        # 1. List tools
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        print(f"Discovered MCP Tools: {tool_names}")
        
        # Verify our greeting tool is discovered
        assert any("greet" in name for name in tool_names), "No greet tool discovered"
        
        # 2. Call tool
        # FastMCP prefixes or modifies the tool names depending on FastAPI routes
        greet_tool_name = [name for name in tool_names if "greet" in name][0]
        
        print(f"\nCalling tool '{greet_tool_name}' with arguments: {{'name': 'Bob', 'shout': True}}")
        result = await client.call_tool(greet_tool_name, {"name": "Bob", "shout": True})
        
        # Access the text content returned
        print(f"Result content: {result.content[0].text}")
        
        print("\n[SUCCESS] Hybrid Server Template tests passed!")
        print("==================================================\n")

if __name__ == "__main__":
    asyncio.run(test_hybrid_server())
