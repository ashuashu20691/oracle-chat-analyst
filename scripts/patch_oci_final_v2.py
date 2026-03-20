#!/usr/bin/env python3
"""
FINAL patch: Replace adapt_messages_to_generic_oci_standard (lines 1315-1447)
with a version that uses globally unique tool_call_ids.
"""

TRANSFORM_PATH = (
    "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/"
    "site-packages/litellm/llms/oci/chat/transformation.py"
)

REPLACEMENT = '''def adapt_messages_to_generic_oci_standard(
    messages: List[AllMessageValues],
) -> List[OCIMessage]:
    """
    Convert OpenAI-format messages to OCI generic format.
    Uses globally unique tool_call_ids across the entire conversation.
    """
    import logging
    logger = logging.getLogger("litellm.oci.tool_id_fix")

    # Debug log incoming messages
    logger.debug("=== adapt_messages input ===")
    for mi, m in enumerate(messages):
        logger.debug(f"  [{mi}] role={m.get('role')} tcid={m.get('tool_call_id')} has_tc={bool(m.get('tool_calls'))} content={str(m.get('content',''))[:80]}")
        if m.get('tool_calls'):
            for t in m.get('tool_calls', []):
                if isinstance(t, dict):
                    logger.debug(f"       tc: id={t.get('id')} func={t.get('function',{}).get('name')}")

    # STEP 1: Normalize tool_call_ids with a GLOBAL counter
    normalized_messages = []
    global_idx = 0

    i = 0
    while i < len(messages):
        msg = messages[i]
        role = msg.get("role")

        if role == "assistant" and msg.get("tool_calls"):
            tool_calls = msg.get("tool_calls", [])

            id_mapping = {}
            normalized_tool_calls = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    new_tc = dict(tc)
                    old_id = tc.get("id", "")
                    new_id = f"call_{global_idx}"
                    id_mapping[old_id] = new_id
                    new_tc["id"] = new_id
                    normalized_tool_calls.append(new_tc)
                    logger.debug(f"ID map: '{old_id}' -> '{new_id}'")
                    global_idx += 1
                else:
                    normalized_tool_calls.append(tc)

            norm_msg = dict(msg)
            norm_msg["tool_calls"] = normalized_tool_calls
            normalized_messages.append(norm_msg)

            # Consume following tool responses
            num_tc = len(normalized_tool_calls)
            found = 0
            j = i + 1

            while j < len(messages) and messages[j].get("role") == "tool":
                tool_msg = dict(messages[j])
                old_tcid = tool_msg.get("tool_call_id", "")

                if old_tcid in id_mapping:
                    tool_msg["tool_call_id"] = id_mapping[old_tcid]
                elif found < num_tc:
                    tool_msg["tool_call_id"] = normalized_tool_calls[found]["id"]

                normalized_messages.append(tool_msg)
                found += 1
                j += 1

            # Only add dummies for HISTORICAL gaps (not the last pending tool call)
            if found < num_tc and j < len(messages):
                for k in range(found, num_tc):
                    normalized_messages.append({
                        "role": "tool",
                        "tool_call_id": normalized_tool_calls[k]["id"],
                        "content": "[No output]"
                    })

            i = j
        else:
            normalized_messages.append(msg)
            i += 1

    # Debug log normalized
    logger.debug("=== normalized output ===")
    for mi, m in enumerate(normalized_messages):
        logger.debug(f"  [{mi}] role={m.get('role')} tcid={m.get('tool_call_id')} has_tc={bool(m.get('tool_calls'))}")

    # STEP 2: Convert to OCI format
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

def main():
    print(f"Reading: {TRANSFORM_PATH}")
    with open(TRANSFORM_PATH, 'r') as f:
        lines = f.readlines()

    # Replace lines 1315-1447 (0-indexed: 1314-1446)
    start = 1314  # line 1315 (0-indexed)
    end = 1447    # line 1448 (exclusive, 0-indexed)

    # Verify we're replacing the right thing
    if "def adapt_messages_to_generic_oci_standard(" not in lines[start]:
        print(f"ERROR: Line {start+1} doesn't contain the function. Got: {lines[start].strip()}")
        return
    if "def adapt_tool_definition_to_oci_standard" not in lines[end]:
        print(f"ERROR: Line {end+1} doesn't contain next function. Got: {lines[end].strip()}")
        return

    print(f"  Replacing lines {start+1}-{end} ({end-start} lines)")

    new_lines = lines[:start] + [REPLACEMENT] + lines[end:]

    with open(TRANSFORM_PATH, 'w') as f:
        f.writelines(new_lines)

    print("  ✓ Done. Restart LiteLLM.")


if __name__ == "__main__":
    main()
