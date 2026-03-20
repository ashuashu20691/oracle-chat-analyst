# Oracle Chat Analyst

AI-powered Oracle database analysis agent using LibreChat, OCI GenAI, LiteLLM, and SQLcl MCP tools.

## What It Does

A conversational agent that connects to Oracle databases via natural language. Ask questions like "List all users with DBA role" or "Show me the largest tables" — the agent writes and executes SQL through SQLcl MCP tools, then provides analysis with actionable insights.

## Architecture

```
User ↔ LibreChat UI ↔ LangGraph Agent ↔ LiteLLM ↔ OCI GenAI (Gemini 2.5 Flash)
                                ↕
                        SQLcl MCP Server (stdio)
                                ↕
                        Oracle Database
```

## Stack

- **LibreChat** — Chat UI + agent framework (LangGraph-based)
- **LiteLLM** — OpenAI-compatible proxy for OCI GenAI
- **OCI GenAI** — Gemini 2.5 Flash model via Oracle Cloud
- **SQLcl MCP** — Model Context Protocol server for Oracle SQL execution
- **MongoDB** — Conversation storage

## Key Patches

OCI GenAI + LiteLLM require patches for tool calling to work with LangGraph:

1. **Unique tool_call IDs** (`scripts/patch_unique_tool_ids.py`) — OCI GenAI returns tool calls without unique IDs. Without this patch, LangGraph's ToolNode silently skips subsequent tool calls.
2. **finish_reason fix** — Sets `finish_reason: "tool_calls"` when tool calls are present so LangGraph continues the agent loop.
3. **Dummy tool responses** — OCI requires every `toolCalls` message to have a matching tool response. The normalization layer adds `[No output]` placeholders for orphaned tool calls.

## Quick Start

```bash
# 1. Clone with LibreChat
git clone --recurse-submodules git@github.com:ashuashu20691/oracle-chat-analyst.git
# Or clone LibreChat separately into ./LibreChat

# 2. Copy environment config
cp .env.example .env
# Edit .env with your OCI compartment ID, SQLcl path, etc.

# 3. Copy LibreChat overlay configs
cp librechat-config/librechat.yaml LibreChat/
cp librechat-config/create-db-agent.js LibreChat/config/
cp librechat-config/create-user.js LibreChat/config/

# 4. Install & patch
cd LibreChat && npm install && cd ..
pip install litellm  # or pipx install litellm
python3 scripts/patch_unique_tool_ids.py

# 5. Start services
./scripts/start-local.sh

# 6. Create user & agent
cd LibreChat
node config/create-user.js
node config/create-db-agent.js
```

## Project Structure

```
├── .env.example              # Environment template
├── litellm_config.yaml       # LiteLLM proxy config for OCI GenAI
├── docker-compose.yml        # Docker deployment option
├── librechat-config/         # LibreChat overlay configs
│   ├── librechat.yaml        # MCP server + endpoint config
│   ├── create-db-agent.js    # Agent creation script
│   └── create-user.js        # User creation script
├── scripts/
│   ├── start-local.sh        # Start all services locally
│   ├── stop-all.sh           # Stop all services
│   ├── patch_unique_tool_ids.py  # Critical LiteLLM patch
│   ├── test-mcp-direct.js    # Test MCP tools directly
│   ├── test-oci-flow.js      # Test OCI tool call flow
│   └── test-agent-api.js     # End-to-end agent API test
└── LibreChat/                # LibreChat (clone separately)
```

## License

MIT
