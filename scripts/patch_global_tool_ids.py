#!/usr/bin/env python3
"""
Patch LiteLLM OCI transformation to use globally unique tool_call_ids.

Problem: The current normalization resets tool_call_ids to call_0, call_1, etc.
for EACH assistant message. When a conversation has multiple tool-call rounds,
OCI GenAI sees duplicate call_0 IDs and can't match tool responses correctly.

Fix: Use a global counter across the entire conversation so IDs are unique:
  Round 1: call_0, call_1
  Round 2: call_2, call_3
  etc.
"""

import re
import shutil
import sys

TRANSFORM_PATH = (
    "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/"
    "site-packages/litellm/llms/oci/chat/transformation.py"
)

# The old pattern: resets idx per assistant message
OLD_CODE = '''    # First pass: collect all messages and identify tool_call groups
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
                    id_mapping[old_id] = new_id'''

# The new pattern: uses global counter
NEW_CODE = '''    # First pass: collect all messages and identify tool_call groups
    # GLOBAL counter so IDs are unique across the entire conversation
    global_tool_idx = 0
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
                    new_id = f"call_{global_tool_idx}"
                    id_mapping[old_id] = new_id'''

# Also fix the fallback func name mapping and the positional remap
OLD_FUNC_MAP = '''                    # Also map by function name as fallback
                    func_name = tc.get("function", {}).get("name", "")
                    if func_name:
                        id_mapping[f"__func__{func_name}_{idx}"] = new_id
                    
                    new_tc["id"] = new_id
                    normalized_tool_calls.append(new_tc)
                    logger.debug(f"Tool call ID mapping: '{old_id}' -> '{new_id}' (func={func_name})")'''

NEW_FUNC_MAP = '''                    # Also map by function name as fallback
                    func_name = tc.get("function", {}).get("name", "")
                    if func_name:
                        id_mapping[f"__func__{func_name}_{idx}"] = new_id
                    
                    new_tc["id"] = new_id
                    normalized_tool_calls.append(new_tc)
                    logger.debug(f"Tool call ID mapping: '{old_id}' -> '{new_id}' (func={func_name})")
                    global_tool_idx += 1'''

# Fix the positional fallback remap
OLD_POSITIONAL = '''                    # Fallback: assign by position
                    if tool_responses_found < num_tool_calls:
                        new_id = f"call_{tool_responses_found}"'''

NEW_POSITIONAL = '''                    # Fallback: assign by position using the normalized IDs
                    if tool_responses_found < num_tool_calls:
                        new_id = normalized_tool_calls[tool_responses_found]["id"]'''

# Fix dummy response generation
OLD_DUMMY = '''            # If some tool calls didn't get responses, add dummy responses
            if tool_responses_found < num_tool_calls:
                for k in range(tool_responses_found, num_tool_calls):
                    dummy = {
                        "role": "tool",
                        "tool_call_id": f"call_{k}",
                        "content": "[Tool execution completed]"
                    }'''

NEW_DUMMY = '''            # If some tool calls didn't get responses, add dummy responses
            if tool_responses_found < num_tool_calls:
                for k in range(tool_responses_found, num_tool_calls):
                    dummy = {
                        "role": "tool",
                        "tool_call_id": normalized_tool_calls[k]["id"],
                        "content": "[Tool execution completed]"
                    }'''


def main():
    print(f"Reading: {TRANSFORM_PATH}")
    with open(TRANSFORM_PATH, 'r') as f:
        content = f.read()

    # Backup
    backup_path = TRANSFORM_PATH + ".bak_global_ids"
    shutil.copy2(TRANSFORM_PATH, backup_path)
    print(f"Backup: {backup_path}")

    # Apply patches
    patches = [
        ("Global counter", OLD_CODE, NEW_CODE),
        ("Func map + increment", OLD_FUNC_MAP, NEW_FUNC_MAP),
        ("Positional fallback", OLD_POSITIONAL, NEW_POSITIONAL),
        ("Dummy responses", OLD_DUMMY, NEW_DUMMY),
    ]

    for name, old, new in patches:
        if old in content:
            content = content.replace(old, new, 1)
            print(f"  ✓ Applied: {name}")
        else:
            print(f"  ✗ NOT FOUND: {name}")
            # Try to show what's around the expected location
            key_phrase = old[:60].strip()
            if key_phrase in content:
                print(f"    (partial match found for: {key_phrase[:40]}...)")
            sys.exit(1)

    with open(TRANSFORM_PATH, 'w') as f:
        f.write(content)

    print(f"\nPatch applied successfully.")
    print("Restart LiteLLM for changes to take effect.")


if __name__ == "__main__":
    main()
