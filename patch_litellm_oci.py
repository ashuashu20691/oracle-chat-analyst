#!/usr/bin/env python3
"""
Patch LiteLLM OCI provider to handle missing tool call IDs.
This is a workaround for the issue where OCI GenAI returns tool calls without IDs.
"""

import os

# Path to the transformation.py file
transformation_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

# Read the file
with open(transformation_file, 'r') as f:
    content = f.read()

# Find and replace the adapt_tools_to_openai_standard function
old_function = '''def adapt_tools_to_openai_standard(
    tools: List[OCIToolCall],
) -> List[ChatCompletionMessageToolCall]:
    new_tools = []
    for tool in tools:
        new_tool = ChatCompletionMessageToolCall(
            id=tool.id,
            type="function",
            function={
                "name": tool.name,
                "arguments": tool.arguments,
            },
        )
        new_tools.append(new_tool)
    return new_tools'''

new_function = '''def adapt_tools_to_openai_standard(
    tools: List[OCIToolCall],
) -> List[ChatCompletionMessageToolCall]:
    new_tools = []
    for idx, tool in enumerate(tools):
        # Generate ID if missing (OCI GenAI sometimes doesn't provide IDs)
        tool_id = tool.id if tool.id else f"call_{idx}"
        new_tool = ChatCompletionMessageToolCall(
            id=tool_id,
            type="function",
            function={
                "name": tool.name,
                "arguments": tool.arguments,
            },
        )
        new_tools.append(new_tool)
    return new_tools'''

# Replace the function
if old_function in content:
    content = content.replace(old_function, new_function)
    
    # Write back
    with open(transformation_file, 'w') as f:
        f.write(content)
    
    print("✅ Successfully patched adapt_tools_to_openai_standard function")
else:
    print("❌ Could not find the function to patch")
    print("The function may have already been patched or the file structure has changed")
