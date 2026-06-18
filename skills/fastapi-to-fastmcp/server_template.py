import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastmcp import FastMCP

app = FastAPI(
    title="Hybrid FastAPI + FastMCP Template",
    description="A template showcasing standard REST endpoints and MCP tools on a single server.",
    version="1.0.0"
)

# Enable CORS and expose the mcp-session-id header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id"]
)

class GreetRequest(BaseModel):
    name: str = Field(..., example="Alice", description="The name of the person to greet")
    shout: bool = Field(False, description="Whether to SHOUT the greeting")

@app.post("/greet", summary="Greet a person")
def greet(req: GreetRequest):
    """
    Greets a person by name, optionally shouting the greeting.
    """
    message = f"Hello, {req.name}!"
    if req.shout:
        message = message.upper()
    return {"message": message}

# Convert FastAPI app to MCP server AFTER all routes are registered
mcp = FastMCP.from_fastapi(app, name="Hybrid Greet Server")

if __name__ == "__main__":
    # If PORT is specified or 'http' is explicitly in arguments, we run in HTTP/SSE mode
    if os.getenv("PORT") or "http" in sys.argv:
        port = int(os.getenv("PORT", 8080))
        print(f"Starting FastMCP + FastAPI server in HTTP transport mode on port {port} under '/mcp'")
        asyncio.run(
            mcp.run_async(
                transport="http",
                path="/mcp",
                host="0.0.0.0",
                port=port,
            )
        )
    else:
        # Default to stdio mode for local testing, Client.from_script, and Claude Desktop
        print("Starting FastMCP server in STDIO mode")
        mcp.run()
