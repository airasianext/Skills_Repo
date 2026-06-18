---
name: fastapi-to-fastmcp
description: Expert guide for converting a Python FastAPI application into a hybrid FastAPI + FastMCP Model Context Protocol (MCP) server that concurrently exposes standard REST endpoints and LLM tools.
---

# FastAPI to FastMCP Hybrid Migration Guide

This skill provides expert procedural guidance, code templates, and validation techniques for transitioning a standard Python FastAPI application into a hybrid **FastAPI + FastMCP** server. 

A hybrid architecture ensures that standard HTTP/REST clients (e.g., frontends, webhooks, standard backend integrations) and LLM contexts (e.g., Claude Desktop, Cursor, Zed, Gemini CLI) can seamlessly consume and interact with the same underlying business logic without code duplication.

---

## 🎯 Architecture & Goals
1. **Zero Code Duplication:** Keep existing FastAPI routes entirely intact.
2. **Automatic Tool Mapping:** Utilize the `FastMCP.from_fastapi(app)` builder to auto-inspect Pydantic request models, type hints, and docstrings to generate compliant LLM tool schemas.
3. **Dual-Transport Runner:** Expose an **HTTP/SSE** server on production/Cloud Run ports while automatically falling back to **STDIO** for local CLI usage, programmatic testing, or local IDE integrations.
4. **Test-Driven Security:** Implement a programmatic test suite using the FastMCP `Client` to verify route mapping before releasing.

---

## 🛠️ Step-by-Step Transition Workflow

### Step 1: Install Dependencies
Ensure the FastMCP package is added to your Python project dependencies:
```bash
uv add fastmcp
# or using pip
pip install fastmcp
```

### Step 2: Establish the TDD Async Test Harness
Before modifying your main application, write an asynchronous test file `tests/test_mcp_integration.py` to verify that your tools are correctly mapped:

```python
import os
import sys
import asyncio
from fastmcp import Client

# Ensure the root folder is on the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_mcp_tools():
    """
    Spawns the main.py application programmatically in stdio mode
    and asserts that routes have been correctly exposed as MCP tools.
    """
    # Spawns main.py as a subprocess over stdio
    async with Client("main.py") as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        print(f"Discovered Tools: {tool_names}")
        
        # Verify core resource exists as a tool
        assert any("invoice" in name or "your_core_resource" in name for name in tool_names), \
            "Expected core resource endpoints to be converted into MCP tools"

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
```

### Step 3: Configure FastAPI CORS Middleware
Web-based remote MCP clients (like Cursor or custom interfaces) require session ID tracking. You must enable CORS and explicitly expose the `mcp-session-id` header to avoid `400 Session Connection` errors:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id"] # CRITICAL: Fixes MCP 400 session errors
)
```

### Step 4: Map Routes Sequentially (Preventing "Cold Start" Empty Schemas)
> ⚠️ **CRITICAL ORDER OF OPERATIONS:** `FastMCP.from_fastapi(app)` inspects the FastAPI application's routing table *at the exact moment of instantiation*.
>
> If you instantiate `mcp = FastMCP.from_fastapi(app)` at the top of your file before declaring your routes, the MCP server will find **zero** routes and generate an empty toolset!
>
> **Solution:** Always declare your `FastMCP.from_fastapi` conversion at the **very bottom** of your application file, after all routes, middlewares, and custom OpenAPI properties have been fully defined.

```python
# 1. Define all models, middleware, and routes...
@app.post("/invoices")
def create_invoice(req: InvoiceRequest):
    ...

@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    ...

# 2. Convert to FastMCP at the VERY BOTTOM of the file
mcp = FastMCP.from_fastapi(app, name="My Gateway Server")
```

### Step 5: Implement the Dual-Transport Main Execution Block
Replace standard Uvicorn runners in your `__main__` block with a dual execution path. This serves over HTTP (using FastMCP's built-in ASGI server) if a `PORT` environment variable is detected, and falls back to STDIO for local testing/clients:

```python
if __name__ == "__main__":
    import asyncio
    import sys
    
    # Check if we are running in production (Cloud Run sets PORT) or HTTP is explicitly requested
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
        # Default to STDIO mode for local CLI execution, test suites, and Claude Desktop
        print("Starting FastMCP server in STDIO mode")
        mcp.run()
```

---

## 💡 Hard-Won Learnings & Best Practices

### 1. Naming Conventions & Policies
If you plan to protect or govern your MCP tools using a local policy engine (like Gemini CLI's Policy Engine):
- **NEVER use underscores in your server name** (e.g., use `oracle-gateway`, NOT `oracle_gateway`).
- The parser splits Fully Qualified Names (`mcp_server_tool`) on the *first* underscore. An underscore in the server name causes policy rules to misidentify the server identity, causing security rules to fail silently.

### 2. Formatting Request Models
`FastMCP.from_fastapi()` extracts model field descriptions to construct the JSON schema that instructs LLMs how to build tool inputs. To ensure your tools are incredibly easy for LLMs to use, always provide descriptive comments in your Pydantic schemas:

```python
# Recommended: Provide rich descriptions for LLM understanding
class InvoiceRequest(BaseModel):
    entity_code: str = Field(..., description="The 4-character Business Unit short code (e.g. BLID, BLPH, BLMY)")
    amount: float = Field(..., description="The positive floating-point invoice monetary total")
```

### 3. Remote SSE Proxying for Claude Desktop
Claude Desktop does not natively support connecting directly to remote HTTP/SSE endpoints. If you deploy your hybrid server to Cloud Run, you must run an NPM-based bridge locally to proxy the STDIO stream:

```json
{
  "mcpServers": {
    "my-remote-gateway": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://<your-cloud-run-url>/mcp"
      ]
    }
  }
}
```
