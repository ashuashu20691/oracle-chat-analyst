#!/usr/bin/env python3
"""
Patch: Don't inject dummy tool responses for the last assistant message's tool calls.

The normalization code was injecting "[Tool execution completed]" dummy responses
when an assistant message had tool_calls but no corresponding tool responses.
This is correct for HISTORICAL messages (where a tool response went missing),
but WRONG for the LAST assistant message — those tool calls are being actively
executed and the real response hasn't arrived yet. The LLM framework handles
this by not including the last assistant+tool pair in the messages.

Actually, the real issue is simpler: if the last message in the array is an
assistant message with tool_calls and there are no following tool messages,
we should NOT inject dummies — the framework is about to execute those tools.
"""

import shutil

TRANSFORM_PATH = (
    "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/"
    "site-packages/litellm/llms/oci/chat/transformation.py"
)

# The current dummy injection code
OLD_DUMMY = '''            # If some tool calls didn't get responses, add dummy responses
            if tool_responses_found < num_tool_calls:
                for k in range(tool_responses_found, num_tool_calls):
                    dummy = {
                        "role": "tool",
                        "tool_call_id": normalized_tool_calls[k]["id"],
                        "content": "[Tool execution completed]"
                    }
                    normalized_messages.append(dummy)
                    logger.debug(f"Added dummy tool response for call_{k}")'''

# Only inject dummies for non-last assistant messages
NEW_DUMMY = '''            # If some tool calls didn't get responses, add dummy responses
            # BUT only for historical messages, not the last assistant message
            # (the last one's tools are being actively executed)
            is_last_assistant = (j >= len(messages))  # no more messages after tool responses
            if tool_responses_found < num_tool_calls and not is_last_assistant:
                for k in range(tool_responses_found, num_tool_calls):
                    dummy = {
                        "role": "tool",
                        "tool_call_id": normalized_tool_calls[k]["id"],
                        "content": "[Tool execution completed]"
                    }
                    normalized_messages.append(dummy)
                    logger.debug(f"Added dummy tool response for {normalized_tool_calls[k]['id']}")
            elif tool_responses_found < num_tool_calls and is_last_assistant:
                logger.debug(f"Skipping dummy injection for last assistant message (tools being executed)")'''


def main():
    print(f"Reading: {TRANSFORM_PATH}")
    with open(TRANSFORM_PATH, 'r') as f:
        content = f.read()

    backup_path = TRANSFORM_PATH + ".bak_no_dummy"
    shutil.copy2(TRANSFORM_PATH, backup_path)
    print(f"Backup: {backup_path}")

    if OLD_DUMMY in content:
        content = content.replace(OLD_DUMMY, NEW_DUMMY, 1)
        print("  ✓ Applied: Skip dummy for last assistant message")
    else:
        print("  ✗ NOT FOUND: dummy injection code")
        print("  Searching for partial match...")
        if "Tool execution completed" in content:
            print("  Found 'Tool execution completed' in file")
        return

    with open(TRANSFORM_PATH, 'w') as f:
        f.write(content)

    print("\nPatch applied. Restart LiteLLM.")


if __name__ == "__main__":
    main()
