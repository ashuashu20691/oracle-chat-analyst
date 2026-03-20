# Fix: Agent Streaming Error

## Problem
The agent is encountering an error when trying to call MCP tools:
```
litellm.APIError: Error building chunks for logging/streaming usage calculation
```

## Root Cause
LibreChat agents use streaming responses by default, but LiteLLM is having issues building streaming chunks for OCI GenAI models. This is a known issue with OCI streaming in LiteLLM.

## Solution: Disable Streaming in Agent Configuration

You need to disable streaming for your SQL Explorer agent in the LibreChat UI:

### Steps:

1. **Open LibreChat** in your browser (http://localhost:3080)

2. **Navigate to Agents**:
   - Click on the "Agents" tab in the left sidebar
   - Find your "SQL Explorer" agent

3. **Edit the Agent**:
   - Click on the agent to open its configuration
   - Look for "Model Parameters" or "Advanced Settings" section

4. **Add Disable Streaming Parameter**:
   - In the Model Parameters section, add:
     ```json
     {
       "disableStreaming": true
     }
     ```
   - Or if there's a UI toggle, enable "Disable Streaming"

5. **Save the Agent Configuration**

6. **Test the Agent**:
   - Start a new conversation with the agent
   - Try asking it to list database connections
   - The agent should now work without streaming errors

## Alternative: Update LiteLLM Configuration

If you prefer to keep streaming enabled, you can try updating to the latest version of LiteLLM which may have fixes for OCI streaming:

```bash
pipx upgrade litellm
```

Then restart the services:
```bash
./scripts/stop-all.sh
./scripts/start-local.sh
```

## Verification

After disabling streaming, the agent should:
1. Successfully call the `list-connections` MCP tool
2. Display available database connections
3. Be able to connect to a database using the `connect` tool
4. Execute SQL queries without errors

## Current Configuration

The following configurations have been updated:

1. **litellm_config.yaml**: Added `stream: false` at model level
2. **LibreChat/librechat.yaml**: Agents interface enabled
3. **OCI Credentials**: Properly configured with explicit credentials

The final step is to disable streaming in the agent's model parameters through the UI.
