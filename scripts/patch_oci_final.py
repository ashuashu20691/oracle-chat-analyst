#!/usr/bin/env python3
"""
FINAL clean patch for OCI GenAI tool_call_id handling.

Root cause: OCI GenAI requires globally unique tool_call_ids across the entire
conversation. LiteLLM's normalization resets IDs per assistant message (call_0, 
call_1 per message), causing duplicates across rounds.

Fix:
1. Use a global counter for tool_call_ids (call_0, call_1, call_2... across ALL messages)
2. Properly remap tool response IDs to match
3. For the LAST assistant message with no tool responses yet: keep it as-is
   (no dummies, no stripping — the agent framework needs it)
"""

import shutil

TRANSFORM_PATH = (
    "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/"
    "site-packages/litellm/llms/oci/chat/transformation.py"
)

OLD_FUNCTION = '''def adapt_messages_to_generic_oci_standard(
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
    messages = normalized_messages'''

NEW_FUNCTION = '''def adapt_messages_to_generic_oci_standard(
    messages: List[AllMessageValues],
) -> List[OCIMessage]:
    """
    Convert OpenAI-format messages to OCI generic format.
    
    Key fix: Use globally unique tool_call_ids across the entire conversation
    so OCI GenAI can correctly match tool responses to tool calls.
    """
    import logging
    logger = logging.getLogger("litellm.oci.tool_id_fix")
    
    # STEP 1: Normalize tool_call_ids with a GLOBAL counter
    normalized_messages = []
    global_idx = 0  # Global counter across ALL assistant messages
    
    i = 0
    while i < len(messages):
        msg = messages[i]
        role = msg.get("role")
        
        if role == "assistant" and msg.get("tool_calls"):
            tool_calls = msg.get("tool_calls", [])
            
            id_mapping = {}  # old_id -> new_id
            normalized_tool_calls = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    new_tc = dict(tc)
                    old_id = tc.get("id", "")
                    new_id = f"call_{global_idx}"
                    id_mapping[old_id] = new_id
                    new_tc["id"] = new_id
                    normalized_tool_calls.append(new_tc)
                    logger.debug(f"Tool call ID: '{old_id}' -> '{new_id}'")
                    global_idx += 1
                else:
                    normalized_tool_calls.append(tc)
            
            norm_msg = dict(msg)
            norm_msg["tool_calls"] = normalized_tool_calls
            normalized_messages.append(norm_msg)
            
            # Consume following tool response messages and remap their IDs
            num_tool_calls = len(normalized_tool_calls)
            tool_responses_found = 0
            j = i + 1
            
            while j < len(messages) and messages[j].get("role") == "tool":
                tool_msg = dict(messages[j])
                old_tool_call_id = tool_msg.get("tool_call_id", "")
                
                if old_tool_call_id in id_mapping:
                    tool_msg["tool_call_id"] = id_mapping[old_tool_call_id]
                elif tool_responses_found < num_tool_calls:
                    # Positional fallback
                    tool_msg["tool_call_id"] = normalized_tool_calls[tool_responses_found]["id"]
                
                normalized_messages.append(tool_msg)
                tool_responses_found += 1
                j += 1
            
            # Add dummy responses ONLY for historical messages missing responses
            # Skip if this is the last assistant message (tools still executing)
            is_last_msg = (j >= len(messages))
            if tool_responses_found < num_tool_calls and not is_last_msg:
                for k in range(tool_responses_found, num_tool_calls):
                    dummy = {
                        "role": "tool",
                        "tool_call_id": normalized_tool_calls[k]["id"],
                        "content": "[No output]"
                    }
                    normalized_messages.append(dummy)
            
            i = j
        else:
            normalized_messages.append(msg)
            i += 1
    
    # STEP 2: Convert normalized messages to OCI format
    messages = normalized_messages'''


def main():
    print(f"Reading: {TRANSFORM_PATH}")
    with open(TRANSFORM_PATH, 'r') as f:
        content = f.read()

    backup_path = TRANSFORM_PATH + ".bak_final"
    shutil.copy2(TRANSFORM_PATH, backup_path)
    print(f"Backup: {backup_path}")

    if OLD_FUNCTION in content:
        content = content.replace(OLD_FUNCTION, NEW_FUNCTION, 1)
        print("  ✓ Applied: Global tool_call_id fix")
    else:
        print("  ✗ NOT FOUND — checking partial matches...")
        if "adapt_messages_to_generic_oci_standard" in content:
            print("  Function exists but exact text doesn't match")
            # Show first few chars around it
            idx = content.index("def adapt_messages_to_generic_oci_standard(\n")
            print(f"  Found at char {idx}")
            print(f"  Preview: {content[idx:idx+200]}")
        return

    with open(TRANSFORM_PATH, 'w') as f:
        f.write(content)

    print("\nDone. Restart LiteLLM.")


if __name__ == "__main__":
    main()
