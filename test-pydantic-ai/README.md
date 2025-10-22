# Pydantic AI Testing Suite

Comprehensive testing suite for Pydantic AI integration with Sentry.

## Agent Types

1. **Customer Support Agent** - Single tool with structured context data
2. **Math Agent** - Multiple calculation tools
3. **MCP Agent** - Connects to MCP server via stdio transport

## Models Tested

- OpenAI: `gpt-4o-mini`
- Anthropic: `claude-3-5-haiku-20241022`

## Methods Tested

- `run_sync()` - Synchronous execution
- `run()` - Async execution  
- `run_stream()` - Streaming responses
- `iter()` - Structured streaming
- `run_stream_events()` - Event streaming

## Running Tests

```bash
./run.sh
```

Set these environment variables:
- `SENTRY_DSN`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

## Test Matrix

The test suite runs all combinations:
- 3 agent types × 2 models × 5 methods = 30 tests

Each agent is created with a unique name like `openai_customer_support_run_sync` or `anthropic_mcp_agent_run` for easy identification in Sentry spans.

## MCP Server

The MCP agent connects to a simple MCP server (`mcp_server.py`) that runs via stdio transport and provides basic calculation and text analysis tools.
