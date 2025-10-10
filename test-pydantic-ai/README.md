# Pydantic AI Sentry Integration Tests

Clean, focused tests for the Sentry Pydantic AI integration.

## Prerequisites

You need to have Python and `curl` installed.

## Configure

Set the following environment variables:
- `SENTRY_DSN`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` (for Anthropic provider tests)

## Run Tests

### Synchronous Tests
```bash
./run.sh
```

### Asynchronous Tests
```bash
./run_async.sh
```

## Test Structure

The tests are organized into three main scenarios, each tested in both sync/async and streaming/non-streaming modes:

### 1. **Simple Agent**
- Basic agent without tools
- Tests fundamental agent functionality
- Demonstrates simple Q&A interactions

### 2. **Agent with Tools**
- Mathematical agent with calculation tools
- Tools: `add()`, `multiply()`, `calculate_percentage()`
- Tests tool integration and structured output
- Returns `CalculationResult` with explanation

### 3. **Two-Agent Workflow**
- **Data Collector Agent**: Extracts and organizes data
- **Data Analyzer Agent**: Analyzes data and provides insights
- Demonstrates agent handoff and workflow patterns
- Returns `AnalysisResult` with findings and recommendations

### 4. **Anthropic Provider Tests**
- **Anthropic Simple Agent**: Basic Claude agent without tools
- **Anthropic Math Agent**: Claude agent with calculation tools
- Tests both OpenAI and Anthropic providers for comparison
- Uses `anthropic:claude-3-5-haiku-20241022` model

## Test Modes

Each scenario is tested in four different modes:

| Mode | Sync/Async | Streaming | Description |
|------|------------|-----------|-------------|
| 1 | Sync | No | `agent.run_sync()` |
| 2 | Sync | Yes | `agent.run_stream_sync()` |
| 3 | Async | No | `await agent.run()` |
| 4 | Async | Yes | `async with agent.run_stream()` |

## Additional Features

### Parallel Processing (Async Only)
- Demonstrates running multiple agents concurrently
- Uses `asyncio.gather()` for parallel execution
- Shows scalable multi-agent patterns

### Model Settings
All agents use optimized model settings:
- **Simple Agent**: Balanced settings (temp: 0.3)
- **Math Agent**: Low temperature for precision (temp: 0.1)
- **Data Collector**: Focused extraction (temp: 0.2)
- **Data Analyzer**: Creative analysis (temp: 0.4)
- **Anthropic Simple Agent**: Balanced settings (temp: 0.3)
- **Anthropic Math Agent**: Low temperature for precision (temp: 0.1)

## Sentry Integration

The integration automatically creates Sentry spans for:
- `gen_ai.pipeline` - Agent workflow execution (root span)
- `gen_ai.invoke_agent` - Individual agent invocations
- `gen_ai.chat` - Model requests (AI client calls)
- `gen_ai.execute_tool` - Tool executions

## File Structure

```
test-pydantic-ai/
├── agents.py           # Agent definitions and tools
├── main.py            # Synchronous tests
├── main_async.py      # Asynchronous tests
├── run.sh             # Run sync tests
├── run_async.sh       # Run async tests
├── pyproject.toml     # Dependencies
└── README.md          # This file
```

## Output Example

```
🚀 Running Pydantic AI Synchronous Tests
==================================================

=== SIMPLE AGENT (Non-Streaming) ===
Question: What is the capital of France?
Answer: The capital of France is Paris.

=== SIMPLE AGENT (Streaming) ===
Question: Tell me a short story about a robot.
Answer (streaming): Once upon a time, a curious robot named Zara discovered...

=== AGENT WITH TOOLS (Non-Streaming) ===
Task: Multi-step calculation
Result: CalculationResult(result=126, operation='multi-step', explanation='...')

=== TWO-AGENT WORKFLOW (Non-Streaming) ===
Step 1: Data Collection
Data Collector Result: Extracted sales data: [150, 200, 175, 225]

Step 2: Data Analysis
Data Analyzer Result: AnalysisResult(summary='...', key_findings=[...], recommendation='...')

==================================================
✅ All synchronous tests completed!
```

This clean structure focuses on the core functionality while thoroughly testing all aspects of the Pydantic AI integration with Sentry.