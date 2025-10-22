# MCP Server Examples with Sentry Integration

This directory contains example [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers with Sentry integration, demonstrating three different API approaches: the standalone FastMCP library, the built-in MCP FastMCP module, and the low-level MCP API.

## 📚 About MCP

The [Model Context Protocol](https://github.com/modelcontextprotocol) is an open protocol that enables seamless integration between LLM applications and external data sources and tools.

## Examples

### 1. FastMCP Library Server (`main_fastmcp.py`)

Uses the standalone [`fastmcp`](https://github.com/jlowin/fastmcp) library - the most modern and feature-rich approach with HTTP support.

**Features:**
- Decorator-based tool, resource, and prompt definitions
- Automatic schema generation from type hints
- Built-in HTTP server support with Starlette
- Context injection support
- Minimal boilerplate code

### 2. MCP Built-in FastMCP Server (`main.py`)

Uses `mcp.server.fastmcp.FastMCP` from the official MCP Python SDK - a simpler high-level API.

**Features:**
- Decorator-based tool, resource, and prompt definitions
- Automatic schema generation
- Context injection support
- STDIO transport only
- Less boilerplate than low-level API

### 3. Low-Level Server (`main_lowlevel.py`)

Uses `mcp.server.lowlevel.Server` from the official MCP Python SDK - provides maximum control.

**Features:**
- Manual schema definitions with full JSON Schema support
- Explicit handler registration
- Fine-grained control over protocol details
- Direct access to MCP types
- Best for complex custom behavior

## Common Features

All three examples demonstrate:

1. **Tools**: Functions that clients can call
   - `calculate_sum` - Add two numbers
   - `calculate_product` - Multiply two numbers
   - `greet_user` - Generate personalized greetings
   - `trigger_error` - Test Sentry error tracking

2. **Resources**: Data endpoints that clients can access
   - `config://settings` - Server configuration
   - `data://users` - User list
   - `data://stats` - Server statistics (low-level only)

3. **Prompts**: Reusable prompt templates
   - `code_review` - Code review template
   - `debug_assistant` - Debugging assistance template
   - `sql_query_helper` - SQL query help (low-level only)

## Running the Servers

### Prerequisites
```bash
# Install dependencies
uv sync
```

### FastMCP Library Server (HTTP)
```bash
# Using the script (automatically starts MCP inspector)
./run_fastmcp.sh

# Or directly (just the server, no inspector)
uv run python main_fastmcp.py
```

This starts an HTTP server on `http://127.0.0.1:8000` that you can interact with via HTTP requests. The `run_fastmcp.sh` script automatically starts the MCP inspector tool for testing.

### MCP Built-in FastMCP Server (STDIO)
```bash
# Using the script (automatically starts MCP inspector)
./run.sh

# Or directly (just the server, no inspector)
uv run python main.py
```

The `run.sh` script automatically starts the MCP inspector tool for testing.

### Low-Level Server (STDIO)
```bash
# Using the script (server only)
./run_lowlevel.sh

# Or directly
uv run python main_lowlevel.py
```

**Note:** The `run_lowlevel.sh` script does NOT automatically start the MCP inspector. To test this server, you need to manually start the inspector:
```bash
npx @modelcontextprotocol/inspector
```

## Using with MCP Clients

The STDIO-based servers (`main.py` and `main_lowlevel.py`) can be used with any MCP-compatible client like [Claude Desktop](https://claude.ai/download).

### Example Client Configuration

For Claude Desktop, add to your configuration file:

**MCP Built-in FastMCP Server:**
```json
{
  "mcpServers": {
    "example-fastmcp": {
      "command": "uv",
      "args": ["run", "python", "/path/to/test-mcp/main.py"],
      "env": {
        "SENTRY_DSN": "your-sentry-dsn-here"
      }
    }
  }
}
```

**Low-Level Server:**
```json
{
  "mcpServers": {
    "example-lowlevel": {
      "command": "uv",
      "args": ["run", "python", "/path/to/test-mcp/main_lowlevel.py"],
      "env": {
        "SENTRY_DSN": "your-sentry-dsn-here"
      }
    }
  }
}
```

**FastMCP Library Server:**

The FastMCP Library server runs as an HTTP server and requires a different client setup that supports HTTP-based MCP connections. Alternatively, you can use it programmatically via HTTP requests.

## Testing with MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a developer tool for testing and debugging MCP servers. It provides an interactive web interface to test your server's tools, resources, and prompts.

### Automatic Inspector Startup

The following run scripts **automatically start the MCP inspector** for you:
- `./run.sh` (MCP Built-in FastMCP server)
- `./run_fastmcp.sh` (FastMCP Library server)

### Manual Inspector Startup

For the **low-level server** (`run_lowlevel.sh`), the inspector is NOT started automatically. You need to manually start it:

```bash
# First, start the server
./run_lowlevel.sh

# Then, in a separate terminal, start the inspector
npx @modelcontextprotocol/inspector
```

### Testing Each Server Implementation Manually

If you prefer to run the inspector manually for any server:

**MCP Built-in FastMCP Server (`main.py`):**
```bash
npx @modelcontextprotocol/inspector uv run python main.py
```

**Low-Level Server (`main_lowlevel.py`):**
```bash
npx @modelcontextprotocol/inspector uv run python main_lowlevel.py
```

**Note:** The FastMCP Library server (`main_fastmcp.py`) runs as an HTTP server and can be tested by navigating to `http://127.0.0.1:8000` in your browser after starting it.

### Using the Inspector

Once the inspector starts, it will:
1. Open a web interface in your browser (typically at `http://localhost:5173`)
2. Connect to your MCP server via STDIO
3. Allow you to interactively test all tools, resources, and prompts
4. Display request/response data for debugging

This is the recommended way to test and debug your MCP servers during development.

## Comparison: FastMCP Library vs MCP Built-in FastMCP vs Low-Level

| Feature | FastMCP Library | MCP Built-in FastMCP | Low-Level |
|---------|-----------------|---------------------|-----------|
| **Package** | `fastmcp` (standalone) | `mcp.server.fastmcp` | `mcp.server.lowlevel` |
| **Code Style** | Decorator-based | Decorator-based | Handler registration |
| **Boilerplate** | Minimal | Minimal | More verbose |
| **Schema** | Auto-generated | Auto-generated | Manual JSON schema |
| **Transport** | HTTP + STDIO | STDIO only | STDIO only |
| **HTTP Support** | ✅ Built-in (Starlette) | ❌ | ❌ |
| **Control** | Medium | Medium | Maximum |
| **Best For** | Modern apps, HTTP APIs | Simple STDIO servers | Complex custom behavior |
| **Learning Curve** | Easy | Easy | Steeper |

### When to Use FastMCP Library
- Modern applications with HTTP support
- Want to expose MCP server over the web
- Need CORS, middleware, or HTTP-specific features
- Prefer the most up-to-date FastMCP implementation

### When to Use MCP Built-in FastMCP
- Simple STDIO-based servers
- Want decorator-based API without external dependencies
- Working with official MCP Python SDK
- Traditional MCP server patterns

### When to Use Low-Level
- Need fine-grained control over protocol
- Custom protocol behavior or validation
- Complex error handling requirements
- Performance-critical applications

**See [COMPARISON.md](./COMPARISON.md) for detailed side-by-side code examples.**

## Sentry Integration

All three examples include Sentry integration using the `MCPIntegration()`. This provides:
- Automatic error tracking for all MCP operations
- Performance monitoring for tool calls
- Breadcrumbs for debugging MCP interactions
- Distributed tracing support

Configure Sentry by setting the `SENTRY_DSN` environment variable.

## Additional Resources

### MCP Documentation & Tools
- [Model Context Protocol Official Site](https://modelcontextprotocol.io/)
- [MCP GitHub Organization](https://github.com/modelcontextprotocol)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Test and debug MCP servers
- [FastMCP Library](https://github.com/jlowin/fastmcp) - Standalone FastMCP with HTTP support
- [MCP Specification](https://spec.modelcontextprotocol.io/)

### Client Applications
- [Claude Desktop](https://claude.ai/download) - Official MCP client from Anthropic
- [MCP Clients List](https://github.com/modelcontextprotocol/servers#clients) - Other MCP-compatible clients

