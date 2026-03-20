#!/usr/bin/env python3
"""
Patches LiteLLM's OCI transformation to add a final validation pass
that ensures EVERY assistant tool_call has a matching tool response,
even if the tool response was not immediately adjacent in the original messages.

This fixes the error:
"An assistant message with 'toolCalls' must be followed by tool messages 
responding to each 'toolCallId'. The following toolCallIds did not have 
response messages: call_0"
"""
import os
import re
import sys

TRANSFORM_PATH = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

def patch():
    if not os.path.exists(TRANSFORM_PATH):
        print(f"ERROR: File not found: {TRANSFORM_PATH}")
        sys.exit(1)

    with open(TRANSFORM_PATH, "r") as f:
        content = f.read()

    # Check if already patched
    if "FINAL VALIDATION PASS" in content:
        print("Already patched. Skipping.")
        return

    # Find the marker after normalization debug logging, before STEP 2
    # We insert a validation pass between normalization and OCI conversion
    old_marker = '    # STEP 2: Convert to OCI format\n    messages = normalized_messages'
    
    if old_marker not in content:
        print("ERROR: Could not find STEP 2 marker in transformation.py")
        print("The file may have been modified. Manual patching required.")
        sys.exit(1)

    new_code = '''    # FINAL VALIDATION PASS: Ensure every assistant tool_call has a matching tool response
    # This catches cases where tool responses are not immediately adjacent
    validated_messages = []
    vi = 0
    while vi < len(normalized_messages):
        msg = normalized_messages[vi]
        role = msg.get("role")
        
        if role == "assistant" and msg.get("tool_calls"):
            validated_messages.append(msg)
            tool_calls = msg.get("tool_calls", [])
            tc_ids = set()
            for tc in tool_calls:
                if isinstance(tc, dict):
                    tc_ids.add(tc.get("id", ""))
            
            # Collect all following tool responses (should be immediately after)
            vj = vi + 1
            responded_ids = set()
            while vj < len(normalized_messages) and normalized_messages[vj].get("role") == "tool":
                tool_msg = normalized_messages[vj]
                responded_ids.add(tool_msg.get("tool_call_id", ""))
                validated_messages.append(tool_msg)
                vj += 1
            
            # Add dummy responses for any missing tool_call_ids
            missing_ids = tc_ids - responded_ids
            for missing_id in sorted(missing_ids):
                validated_messages.append({
                    "role": "tool",
                    "tool_call_id": missing_id,
                    "content": "[No output - auto-inserted]"
                })
                with open(debug_log_path, "a") as dbg:
                    dbg.write(f"  [VALIDATION] Inserted dummy tool response for {missing_id}\\n")
            
            vi = vj
        else:
            validated_messages.append(msg)
            vi += 1
    
    normalized_messages = validated_messages

    # STEP 2: Convert to OCI format
    messages = normalized_messages'''

    content = content.replace(old_marker, new_code)

    with open(TRANSFORM_PATH, "w") as f:
        f.write(content)

    print("SUCCESS: Patched transformation.py with final validation pass")
    print(f"File: {TRANSFORM_PATH}")

if __name__ == "__main__":
    patch()
