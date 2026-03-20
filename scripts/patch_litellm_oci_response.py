#!/usr/bin/env python3
"""
Patch LiteLLM OCI types to handle Gemini model responses that may be missing
'message' in choices and 'completionTokens' in usage.
"""

import os
import sys

oci_types_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/types/llms/oci.py"
)

transformation_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

# --- Patch 1: Make OCIResponseChoice.message optional ---
with open(oci_types_file, 'r') as f:
    content = f.read()

# Backup
with open(oci_types_file + '.bak2', 'w') as f:
    f.write(content)

# Make message optional in OCIResponseChoice
old_choice = '''class OCIResponseChoice(BaseModel):
    """A completion choice in the OCI response."""

    index: int
    message: OCIMessage
    finishReason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None'''

new_choice = '''class OCIResponseChoice(BaseModel):
    """A completion choice in the OCI response."""

    index: int
    message: Optional[OCIMessage] = None
    finishReason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None'''

if old_choice in content:
    content = content.replace(old_choice, new_choice)
    print("✅ Patched OCIResponseChoice.message to be Optional")
else:
    print("⚠️  OCIResponseChoice already patched or structure changed")

# Make completionTokens optional in OCIResponseUsage
old_usage = '''class OCIResponseUsage(BaseModel):
    """Token usage in the OCI response."""

    promptTokens: int
    completionTokens: int
    totalTokens: int'''

new_usage = '''class OCIResponseUsage(BaseModel):
    """Token usage in the OCI response."""

    promptTokens: int = 0
    completionTokens: int = 0
    totalTokens: int = 0'''

if old_usage in content:
    content = content.replace(old_usage, new_usage)
    print("✅ Patched OCIResponseUsage fields to have defaults")
else:
    print("⚠️  OCIResponseUsage already patched or structure changed")

with open(oci_types_file, 'w') as f:
    f.write(content)

# --- Patch 2: Fix _handle_generic_response to handle missing message ---
with open(transformation_file, 'r') as f:
    t_content = f.read()

with open(transformation_file + '.bak2', 'w') as f:
    f.write(t_content)

old_handler = '''        message = model_response.choices[0].message  # type: ignore
        response_message = completion_response.chatResponse.choices[0].message
        if response_message.content and response_message.content[0].type == "TEXT":
            message.content = response_message.content[0].text
        if response_message.toolCalls:
            message.tool_calls = adapt_tools_to_openai_standard(
                response_message.toolCalls
            )'''

new_handler = '''        message = model_response.choices[0].message  # type: ignore
        response_message = completion_response.chatResponse.choices[0].message
        if response_message is not None:
            if response_message.content and response_message.content[0].type == "TEXT":
                message.content = response_message.content[0].text
            if response_message.toolCalls:
                message.tool_calls = adapt_tools_to_openai_standard(
                    response_message.toolCalls
                )'''

if old_handler in t_content:
    t_content = t_content.replace(old_handler, new_handler)
    print("✅ Patched _handle_generic_response for None message handling")
else:
    print("⚠️  _handle_generic_response already patched or structure changed")

# Also fix the usage to handle missing completionTokens
old_usage_handler = '''        usage = Usage(
            prompt_tokens=completion_response.chatResponse.usage.promptTokens,
            completion_tokens=completion_response.chatResponse.usage.completionTokens,
            total_tokens=completion_response.chatResponse.usage.totalTokens,
        )'''

new_usage_handler = '''        usage = Usage(
            prompt_tokens=completion_response.chatResponse.usage.promptTokens or 0,
            completion_tokens=completion_response.chatResponse.usage.completionTokens or 0,
            total_tokens=completion_response.chatResponse.usage.totalTokens or 0,
        )'''

if old_usage_handler in t_content:
    t_content = t_content.replace(old_usage_handler, new_usage_handler)
    print("✅ Patched usage handler for missing token counts")
else:
    print("⚠️  Usage handler already patched or structure changed")

with open(transformation_file, 'w') as f:
    f.write(t_content)

print("\n✅ All patches applied. Restart LiteLLM for changes to take effect.")
