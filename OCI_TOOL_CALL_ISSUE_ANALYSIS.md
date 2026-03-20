# OCI GenAI Tool Call Issue - Analysis

## Current Status

✅ **WORKING**: The `list-connections` tool successfully executes and returns database connections
❌ **FAILING**: Subsequent tool calls fail with message format validation error

## The Problem

When the agent tries to make a second tool call (e.g., `connect`), OCI GenAI rejects the request with:

```
OciException - { "code": "400", "message": "An assistant message with 'toolCalls' must be followed 
by tool messages responding to each 'toolCallId'. The following toolCallIds did not have response 
messages: call_0" }
```

## Root Cause

OCI GenAI has strict requirements for message formatting when using tool calls:

1. **Assistant message with tool_calls** must be immediately followed by
2. **Tool message(s)** with `role="tool"` and `tool_call_id` matching each tool call

### Example of Required Format:

```json
[
  {
    "role": "user",
    "content": "List database connections"
  },
  {
    "role": "assistant",
    "content": null,  // Note: must be null, not empty string
    "tool_calls": [
      {
        "id": "call_0",
        "type": "function",
        "function": {
          "name": "list-connections",
          "arguments": "{}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_0",
    "content": "[database list results]"
  },
  {
    "role": "user",
    "content": "Connect to BASE_DB_23AI"
  }
]
```

### What LibreChat is Doing

LibreChat's agent framework uses LangGraph which:
1. Executes tools internally
2. Stores tool calls and responses in a different format
3. When reconstructing conversation history, doesn't format messages according to OCI GenAI's strict requirements

The `loadPreviousMessages` function in `responses.js` loads messages but doesn't preserve the tool call structure properly for OCI GenAI.

## Why This is Complex

This is a fundamental compatibility issue between:
- **LibreChat's agent framework**: Designed to work with OpenAI, Anthropic, and other providers that are more lenient with message formatting
- **OCI GenAI**: Has strict validation requirements for tool call message sequences

Fixing this would require:
1. Modifying how LibreChat stores messages to preserve tool call structure
2. Updating message loading to reconstruct proper tool call/response pairs
3. Ensuring assistant messages with tool calls have `content: null`
4. Adding tool messages with proper `tool_call_id` references

## Potential Solutions

### Option 1: Use a Different Model Provider (RECOMMENDED)

Switch to OpenAI or Anthropic for the agent, which are more lenient with message formatting and better supported by LibreChat:

**Pros:**
- Immediate solution
- Better LibreChat compatibility
- More mature tool calling support

**Cons:**
- Requires API keys for OpenAI/Anthropic
- Additional cost

### Option 2: Disable Multi-Turn Tool Calling

Configure the agent to only handle single-turn interactions (one tool call per conversation):

**Pros:**
- Works with current setup
- No code changes needed

**Cons:**
- Limited functionality
- Can't chain tool calls (list → connect → query)

### Option 3: Fix LibreChat's OCI Integration (COMPLEX)

Modify LibreChat's agent framework to properly format messages for OCI GenAI:

**Files to modify:**
- `LibreChat/api/server/controllers/agents/responses.js` - `loadPreviousMessages` function
- `LibreChat/api/app/clients/prompts/formatMessages.js` - `formatAgentMessages` function
- Message storage/retrieval to preserve tool call structure

**Pros:**
- Full OCI GenAI compatibility
- Maintains desired architecture

**Cons:**
- Complex changes to LibreChat core
- Risk of breaking other functionality
- Requires deep understanding of LibreChat's agent framework

### Option 4: Use LiteLLM's Message Transformation

Configure LiteLLM to transform messages to OCI GenAI's required format:

**Pros:**
- Centralized fix in LiteLLM
- Doesn't require LibreChat changes

**Cons:**
- May not be supported by LiteLLM
- Would need custom LiteLLM plugin/middleware

## Recommendation

Given the complexity and the fact that this is a deep integration issue, I recommend **Option 1**: Switch to using OpenAI or Anthropic for the agent.

If you must use OCI GenAI, then **Option 3** is the only viable long-term solution, but it requires significant development effort to modify LibreChat's core agent framework.

## Immediate Next Steps

1. **Test with OpenAI**: Configure the agent to use OpenAI's GPT-4 to verify the MCP tools work correctly
2. **Report to LibreChat**: File an issue with LibreChat about OCI GenAI compatibility
3. **Consider alternatives**: Evaluate if OCI GenAI is the right choice for this use case

## Technical Details

- **LiteLLM Version**: 1.82.1
- **LibreChat Version**: 0.8.3
- **OCI GenAI Model**: google.gemini-2.5-flash
- **Issue**: Message format validation for multi-turn tool calling
- **Related PR**: https://github.com/BerriAI/litellm/pull/16899 (fixes tool call ID generation but doesn't fix message format)
