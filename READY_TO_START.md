# Ready to Start!

All dependencies are installed and configured. Now run:

```bash
./scripts/start-local.sh
```

This will:
1. Start LiteLLM proxy (port 4000)
2. Start LibreChat backend and frontend (port 3080)
3. SQLcl MCP will be managed automatically by LibreChat

Then open: **http://localhost:3080**

## What's Configured

✅ LiteLLM with OCI GenAI (Gemini 2.5 Flash)
✅ SQLcl MCP Server (stdio mode)
✅ LibreChat with artifacts enabled
✅ All packages built

## If You See Errors

Check the logs:
```bash
tail -f logs/litellm.log
tail -f logs/librechat-backend.log
```

Stop all services:
```bash
./scripts/stop-all.sh
```
