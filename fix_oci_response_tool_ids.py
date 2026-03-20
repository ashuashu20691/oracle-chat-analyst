#!/usr/bin/env python3
"""
Fix OCI GenAI response parsing to handle tool calls without IDs.
This patches LiteLLM to add IDs to tool calls in responses before Pydantic validation.
"""

import os

# Path to the transformation.py file
transformation_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

# Read the file
with open(transformation_file, 'r') as f:
    content = f.read()

# Find the _handle_generic_response function and fix tool call ID handling
old_code = '''    def _handle_generic_response(
        self,
        json: dict,
        model: str,
        model_response: ModelResponse,
        raw_response: httpx.Response
    ) -> ModelResponse:
        """Handle generic OCI response format."""
        try:
            completion_response = OCICompletionResponse(**json)'''

new_code = '''    def _handle_generic_response(
        self,
        json: dict,
        model: str,
        model_response: ModelResponse,
        raw_response: httpx.Response
    ) -> ModelResponse:
        """Handle generic OCI response format."""
        # Fix tool calls without IDs before Pydantic validation
        if "chatResponse" in json and "choices" in json["chatResponse"]:
            for choice in json["chatResponse"]["choices"]:
                if "message" in choice and "toolCalls" in choice["message"]:
                    tool_calls = choice["message"]["toolCalls"]
                    if tool_calls:
                        for idx, tool_call in enumerate(tool_calls):
                            if isinstance(tool_call, dict) and "id" not in tool_call:
                                tool_call["id"] = f"call_{idx}"
        
        try:
            completion_response = OCICompletionResponse(**json)'''

# Replace the code
if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Write back
    with open(transformation_file, 'w') as f:
        f.write(content)
    
    print("✅ Successfully patched _handle_generic_response function")
    print("   Added tool call ID generation for responses")
else:
    print("❌ Could not find the function to patch")
    print("The function may have already been patched or the file structure has changed")
