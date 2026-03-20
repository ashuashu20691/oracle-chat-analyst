#!/usr/bin/env python3
"""
Fix OCI GenAI message formatting to ensure tool calls are followed by tool responses.
This patches LiteLLM to properly handle LibreChat's message format.
"""

import os

# Path to the transformation.py file
transformation_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

# Read the file
with open(transformation_file, 'r') as f:
    content = f.read()

# Find the adapt_messages_to_generic_oci_standard function and add message validation/fixing
old_function_start = '''def adapt_messages_to_generic_oci_standard(
    messages: List[AllMessageValues],
) -> List[OCIMessage]:
    new_messages = []
    for message in messages:'''

new_function_start = '''def adapt_messages_to_generic_oci_standard(
    messages: List[AllMessageValues],
) -> List[OCIMessage]:
    # Fix message format: ensure assistant messages with tool_calls are followed by tool responses
    fixed_messages = []
    pending_tool_calls = {}  # Track tool calls that need responses
    
    for i, message in enumerate(messages):
        role = message.get("role")
        tool_calls = message.get("tool_calls")
        tool_call_id = message.get("tool_call_id")
        
        # Track assistant messages with tool calls
        if role == "assistant" and tool_calls:
            for tool_call in tool_calls:
                if isinstance(tool_call, dict) and "id" in tool_call:
                    pending_tool_calls[tool_call["id"]] = True
        
        # Mark tool responses as handled
        if role == "tool" and tool_call_id:
            if tool_call_id in pending_tool_calls:
                del pending_tool_calls[tool_call_id]
        
        fixed_messages.append(message)
    
    # If there are pending tool calls without responses, add dummy responses
    # This prevents OCI GenAI from rejecting the request
    if pending_tool_calls:
        # Find the last assistant message with tool calls
        for i in range(len(fixed_messages) - 1, -1, -1):
            msg = fixed_messages[i]
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                # Add tool response messages after this assistant message
                insert_pos = i + 1
                for tool_call in msg.get("tool_calls", []):
                    if isinstance(tool_call, dict) and tool_call.get("id") in pending_tool_calls:
                        # Insert a tool response message
                        tool_response = {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": "[Tool execution completed]"
                        }
                        fixed_messages.insert(insert_pos, tool_response)
                        insert_pos += 1
                break
    
    messages = fixed_messages
    new_messages = []
    for message in messages:'''

# Replace the function start
if old_function_start in content:
    content = content.replace(old_function_start, new_function_start)
    
    # Write back
    with open(transformation_file, 'w') as f:
        f.write(content)
    
    print("✅ Successfully patched adapt_messages_to_generic_oci_standard function")
    print("   Added message validation to ensure tool calls have responses")
else:
    print("❌ Could not find the function to patch")
    print("The function may have already been patched or the file structure has changed")
