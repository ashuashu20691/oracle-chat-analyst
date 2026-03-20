#!/usr/bin/env python3
"""
Patch: Strip pending tool calls from messages sent to OCI GenAI.

Problem: LibreChat's agent framework sends the full conversation history to the LLM,
including the last assistant message with tool_calls BEFORE the tool response arrives.
Most LLMs handle this gracefully, but OCI GenAI strictly requires every assistant
message with toolCalls to be followed by matching tool response messages.

Fix: In adapt_messages_to_generic_oci_standard, if the last message is an assistant
message with tool_calls and there are no following tool responses, strip it from
the messages before sending to OCI.
"""

import shutil

TRANSFORM_PATH = (
    "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/"
    "site-packages/litellm/llms/oci/chat/transformation.py"
)

# Find the start of the normalization function and add the strip logic
# right at the beginning, before any other processing
OLD_START = '''    """
    Convert OpenAI-format messages to OCI generic format.
    
    Key fix: Normalize tool_call_ids to ensure assistant tool_calls and tool response
    messages always have matching IDs, regardless of what IDs the client sends.
    """
    import logging
    logger = logging.getLogger("litellm.oci.tool_id_fix")'''

NEW_START = '''    """
    Convert OpenAI-format messages to OCI generic format.
    
    Key fix: Normalize tool_call_ids to ensure assistant tool_calls and tool response
    messages always have matching IDs, regardless of what IDs the client sends.
    Also strips pending tool calls (last assistant message with tool_calls but no
    following tool responses) since OCI GenAI strictly requires matching responses.
    """
    import logging
    logger = logging.getLogger("litellm.oci.tool_id_fix")
    
    # CRITICAL FIX: Strip pending tool calls from the end of the conversation.
    # If the last message is an assistant with tool_calls and no tool responses follow,
    # OCI GenAI will reject it. Remove it so the LLM can re-generate the tool call.
    while len(messages) > 0:
        last_msg = messages[-1]
        if last_msg.get("role") == "assistant" and last_msg.get("tool_calls"):
            logger.debug(f"Stripping pending tool call from end of messages (func={last_msg.get('tool_calls', [{}])[0].get('function', {}).get('name', '?')})")
            messages = list(messages[:-1])  # make a copy without the last message
        else:
            break'''


def main():
    print(f"Reading: {TRANSFORM_PATH}")
    with open(TRANSFORM_PATH, 'r') as f:
        content = f.read()

    backup_path = TRANSFORM_PATH + ".bak_strip_pending"
    shutil.copy2(TRANSFORM_PATH, backup_path)
    print(f"Backup: {backup_path}")

    if OLD_START in content:
        content = content.replace(OLD_START, NEW_START, 1)
        print("  ✓ Applied: Strip pending tool calls")
    else:
        print("  ✗ NOT FOUND")
        # Debug
        if "Key fix: Normalize tool_call_ids" in content:
            print("  Found the docstring but exact match failed")
        return

    with open(TRANSFORM_PATH, 'w') as f:
        f.write(content)

    print("\nPatch applied. Restart LiteLLM.")


if __name__ == "__main__":
    main()
