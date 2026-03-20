#!/usr/bin/env python3
"""
Fix: Always add dummy tool responses for orphaned tool_calls,
including the LAST assistant message (pending tool call from LibreChat).

The previous patch skipped the last message with `j < len(messages)`.
OCI GenAI requires every toolCall to have a matching tool response.
"""

TRANSFORM_PATH = (
    "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/"
    "site-packages/litellm/llms/oci/chat/transformation.py"
)

OLD = '            # Only add dummies for HISTORICAL gaps (not the last pending tool call)\n            if found < num_tc and j < len(messages):'

NEW = '            # Always add dummies for ANY missing tool responses (OCI requires it)\n            if found < num_tc:'

def main():
    with open(TRANSFORM_PATH, 'r') as f:
        content = f.read()

    if OLD not in content:
        print("ERROR: Could not find the target code to patch.")
        print("Looking for:")
        print(repr(OLD))
        return False

    content = content.replace(OLD, NEW)

    with open(TRANSFORM_PATH, 'w') as f:
        f.write(content)

    print("✓ Patched: Now always adds dummy tool responses for orphaned tool_calls")
    return True

if __name__ == "__main__":
    main()
