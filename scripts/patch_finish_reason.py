#!/usr/bin/env python3
"""
Patch LiteLLM OCI transformation to set finish_reason = "tool_calls"
when the response contains tool calls.

Without this fix, OCI GenAI returns finish_reason "stop" even when tool calls
are present. LangGraph (LibreChat's agent framework) uses finish_reason to
decide whether to continue the tool execution loop. When it sees "stop", it
thinks the LLM is done and never sends the tool results back.
"""

import re
import sys

TRANSFORM_FILE = "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"

def patch():
    with open(TRANSFORM_FILE, "r") as f:
        content = f.read()

    # === FIX 1: _handle_generic_response ===
    # After tool_calls are set on the message, set finish_reason = "tool_calls"
    old_generic = """            if response_message.toolCalls:
                message.tool_calls = adapt_tools_to_openai_standard(
                    response_message.toolCalls
                )"""

    new_generic = """            if response_message.toolCalls:
                message.tool_calls = adapt_tools_to_openai_standard(
                    response_message.toolCalls
                )
                # PATCH: Set finish_reason to "tool_calls" so LangGraph continues the loop
                model_response.choices[0].finish_reason = "tool_calls"  # type: ignore"""

    if old_generic not in content:
        if 'model_response.choices[0].finish_reason = "tool_calls"' in content:
            print("FIX 1 (_handle_generic_response): Already patched.")
        else:
            print("FIX 1 (_handle_generic_response): ERROR - Could not find target code!")
            sys.exit(1)
    else:
        content = content.replace(old_generic, new_generic)
        print("FIX 1 (_handle_generic_response): Patched finish_reason for tool_calls.")

    # === FIX 2: _handle_cohere_response (Cohere path) ===
    # The Cohere path also doesn't set finish_reason = "tool_calls"
    old_cohere = """        if cohere_response.chatResponse.toolCalls:
            tool_calls = []
            for tool_call in cohere_response.chatResponse.toolCalls:
                tool_calls.append({
                    "id": f"call_{len(tool_calls)}",  # Generate a simple ID
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.parameters)
                    }
                })"""

    new_cohere = """        if cohere_response.chatResponse.toolCalls:
            tool_calls = []
            for tool_call in cohere_response.chatResponse.toolCalls:
                tool_calls.append({
                    "id": f"call_{len(tool_calls)}",  # Generate a simple ID
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.parameters)
                    }
                })
            # PATCH: Override finish_reason when tool calls are present
            finish_reason = "tool_calls"  """

    if old_cohere not in content:
        if '# PATCH: Override finish_reason when tool calls are present' in content:
            print("FIX 2 (_handle_cohere_response): Already patched.")
        else:
            print("FIX 2 (_handle_cohere_response): WARNING - Could not find Cohere target (may not be needed).")
    else:
        content = content.replace(old_cohere, new_cohere)
        print("FIX 2 (_handle_cohere_response): Patched finish_reason for tool_calls.")

    with open(TRANSFORM_FILE, "w") as f:
        f.write(content)

    print("\nDone. Restart LiteLLM for changes to take effect.")

if __name__ == "__main__":
    patch()
