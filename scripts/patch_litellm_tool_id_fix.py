#!/usr/bin/env python3
"""
Patch LiteLLM OCI transformation to fix tool_call_id mismatch.

Problem: OCI GenAI returns tool calls without IDs. LiteLLM generates 'call_0', 'call_1' etc.
But when LibreChat sends the conversation history back, the tool response messages may have
different tool_call_ids than what the assistant message's tool_calls have. This causes OCI
GenAI to reject the request with:
  "An assistant message with 'toolCalls' must be followed by tool messages responding to 
   each 'toolCallId'. The following toolCallIds did not have response messages: call_0"

Fix: In adapt_messages_to_generic_oci_standard, normalize tool_call_ids by:
1. For each assistant message with tool_calls, assign sequential IDs (call_0, call_1, etc.)
2. Map the NEXT tool response messages to use those same sequential IDs
This ensures perfect matching regardless of what IDs LibreChat sends.
"""

import os
import shutil

transformation_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

with open(transformation_file, 'r') as f:
    content = f.read()

# Backup
backup_file = transformation_file + '.bak_toolid_fix'
shutil.copy2(transformation_file, backup_file)
print(f"✅ Backup saved to {backup_file}")

# Replace the entire adapt_messages_to_generic_oci_standard function
old_function = '''def adapt_messages_to_generic_oci_standard(
    messages: List[AllMessageValues],
) -> List[OCIMessage]:
    # Fix message format: ensure assistant messages with tool_calls are followed by tool respons'''

# Find the end of the function (it ends before adapt_tool_definition_to_oci_standard)
old_func_end = '''def adapt_tool_definition_to_oci_standard(tools: List[Dict], vendor: OCIVendors):'''

# Find the start and end positions
start_pos = content.find(old_function)
end_pos = content.find(old_func_end)

if start_pos == -1:
    print("❌ Could not find adapt_messages_to_generic_oci_standard function start")
    exit(1)
if end_pos == -1:
    print("❌ Could not find adapt_tool_definition_to_oci_standard function start")
    exit(1)

new_function = '''def adapt_messages_to_generic_oci_standard(
    messages: List[AllMessageValues],
) -> List[OCIMessage]:
    """
    Convert OpenAI-format messages to OCI generic format.
    
    Key fix: Normalize tool_call_ids to ensure assistant tool_calls and tool response
    messages always have matching IDs, regardless of what IDs the client sends.
    """
    import logging
    logger = logging.getLogger("litellm.oci.tool_id_fix")
    
    # STEP 1: Normalize tool_call_ids across the conversation
    # Build a mapping: for each assistant message with tool_calls, assign sequential IDs
    # and remap the corresponding tool response messages to use those same IDs
    normalized_messages = []
    
    # First pass: collect all messages and identify tool_call groups
    i = 0
    while i < len(messages):
        msg = messages[i]
        role = msg.get("role")
        
        if role == "assistant" and msg.get("tool_calls"):
            tool_calls = msg.get("tool_calls", [])
            
            # Assign normalized IDs to this assistant message's tool calls
            id_mapping = {}  # old_id -> new_id
            normalized_tool_calls = []
            for idx, tc in enumerate(tool_calls):
                if isinstance(tc, dict):
                    new_tc = dict(tc)
                    old_id = tc.get("id", "")
                    new_id = f"call_{idx}"
                    id_mapping[old_id] = new_id
                    
                    # Also map by function name as fallback
                    func_name = tc.get("function", {}).get("name", "")
                    if func_name:
                        id_mapping[f"__func__{func_name}_{idx}"] = new_id
                    
                    new_tc["id"] = new_id
                    normalized_tool_calls.append(new_tc)
                    logger.debug(f"Tool call ID mapping: '{old_id}' -> '{new_id}' (func={func_name})")
                else:
                    normalized_tool_calls.append(tc)
            
            # Create normalized assistant message
            norm_msg = dict(msg)
            norm_msg["tool_calls"] = normalized_tool_calls
            normalized_messages.append(norm_msg)
            
            # Now consume the following tool response messages and remap their IDs
            num_tool_calls = len(normalized_tool_calls)
            tool_responses_found = 0
            j = i + 1
            
            while j < len(messages) and messages[j].get("role") == "tool":
                tool_msg = dict(messages[j])
                old_tool_call_id = tool_msg.get("tool_call_id", "")
                
                # Try to map the tool_call_id
                if old_tool_call_id in id_mapping:
                    tool_msg["tool_call_id"] = id_mapping[old_tool_call_id]
                    logger.debug(f"Remapped tool response ID: '{old_tool_call_id}' -> '{id_mapping[old_tool_call_id]}'")
                else:
                    # Fallback: assign by position
                    if tool_responses_found < num_tool_calls:
                        new_id = f"call_{tool_responses_found}"
                        logger.debug(f"Positional remap tool response ID: '{old_tool_call_id}' -> '{new_id}'")
                        tool_msg["tool_call_id"] = new_id
                    else:
                        logger.warning(f"Extra tool response with ID '{old_tool_call_id}' - no matching tool call")
                
                normalized_messages.append(tool_msg)
                tool_responses_found += 1
                j += 1
            
            # If some tool calls didn't get responses, add dummy responses
            if tool_responses_found < num_tool_calls:
                for k in range(tool_responses_found, num_tool_calls):
                    dummy = {
                        "role": "tool",
                        "tool_call_id": f"call_{k}",
                        "content": "[Tool execution completed]"
                    }
                    normalized_messages.append(dummy)
                    logger.debug(f"Added dummy tool response for call_{k}")
            
            i = j  # Skip past the tool responses we already processed
        else:
            normalized_messages.append(msg)
            i += 1
    
    # STEP 2: Convert normalized messages to OCI format
    messages = normalized_messages
    new_messages = []
    for message in messages:
        role = message["role"]
        content = message.get("content")
        tool_calls = message.get("tool_calls")
        tool_call_id = message.get("tool_call_id")

        if role == "assistant" and tool_calls is not None:
            if not isinstance(tool_calls, list):
                raise Exception("Prop `tool_calls` must be a list of tool calls")
            new_messages.append(
                adapt_messages_to_generic_oci_standard_tool_call(role, tool_calls)
            )

        elif role in ["system", "user", "assistant"] and content is not None:
            if not isinstance(content, (str, list)):
                raise Exception(
                    "Prop `content` must be a string or a list of content items"
                )
            new_messages.append(
                adapt_messages_to_generic_oci_standard_content_message(role, content)
            )

        elif role == "tool":
            if not isinstance(tool_call_id, str):
                raise Exception("Prop `tool_call_id` is required and must be a string")
            if not isinstance(content, str):
                content = str(content) if content is not None else "[No content]"
            new_messages.append(
                adapt_messages_to_generic_oci_standard_tool_response(
                    role, tool_call_id, content
                )
            )

    return new_messages


'''

# Replace the function
content = content[:start_pos] + new_function + content[end_pos:]

with open(transformation_file, 'w') as f:
    f.write(content)

print("✅ Successfully patched adapt_messages_to_generic_oci_standard with tool_call_id normalization fix")
print("\nRestart LiteLLM for changes to take effect.")
