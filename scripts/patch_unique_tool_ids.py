#!/usr/bin/env python3
"""
Patch LiteLLM OCI transformation to use globally unique tool_call IDs in responses.

ROOT CAUSE: OCI GenAI returns tool calls without IDs (or with non-unique IDs).
LiteLLM generates IDs like call_0, call_1 per response. But LangGraph's ToolNode
filters tool calls by checking if a ToolMessage with the same tool_call_id already
exists in the conversation. When two different responses both generate call_0,
the second tool call gets filtered out as "already processed".

FIX: Use uuid4-based IDs so every tool call across the entire conversation is unique.
"""
import re

TRANSFORM_PATH = "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"

with open(TRANSFORM_PATH, "r") as f:
    content = f.read()

# Fix 1: adapt_tools_to_openai_standard - used for generic (non-Cohere) responses
# Replace: tool_id = tool.id if tool.id else f"call_{idx}"
# With: tool_id = tool.id if tool.id else f"call_{uuid.uuid4().hex[:12]}"
old_adapt = 'tool_id = tool.id if tool.id else f"call_{idx}"'
new_adapt = '''tool_id = tool.id if tool.id else f"call_{__import__('uuid').uuid4().hex[:12]}"'''
assert old_adapt in content, f"Could not find adapt_tools pattern"
content = content.replace(old_adapt, new_adapt)

# Fix 2: _handle_generic_response - pre-validation ID fix
# Replace: tool_call["id"] = f"call_{idx}"
# With: tool_call["id"] = f"call_{__import__('uuid').uuid4().hex[:12]}"
old_generic = 'tool_call["id"] = f"call_{idx}"'
new_generic = '''tool_call["id"] = f"call_{__import__(\\'uuid\\').uuid4().hex[:12]}"'''
# This one is trickier because of escaping. Let me use a different approach.

# Actually let me just do both replacements more carefully
# Reset and do it properly
with open(TRANSFORM_PATH, "r") as f:
    content = f.read()

# Count occurrences
count1 = content.count('tool_id = tool.id if tool.id else f"call_{idx}"')
count2 = content.count('tool_call["id"] = f"call_{idx}"')
count3 = content.count('"id": f"call_{len(tool_calls)}"')

print(f"Found {count1} occurrences of adapt_tools pattern")
print(f"Found {count2} occurrences of generic_response pattern")
print(f"Found {count3} occurrences of cohere_response pattern")

# Fix 1: adapt_tools_to_openai_standard
content = content.replace(
    'tool_id = tool.id if tool.id else f"call_{idx}"',
    'tool_id = tool.id if tool.id else f"call_{__import__(\'uuid\').uuid4().hex[:12]}"'
)

# Fix 2: _handle_generic_response pre-validation
content = content.replace(
    'tool_call["id"] = f"call_{idx}"',
    'tool_call["id"] = f"call_{__import__(\'uuid\').uuid4().hex[:12]}"'
)

# Fix 3: _handle_cohere_response
content = content.replace(
    '"id": f"call_{len(tool_calls)}"',
    '"id": f"call_{__import__(\'uuid\').uuid4().hex[:12]}"'
)

with open(TRANSFORM_PATH, "w") as f:
    f.write(content)

print("Patch applied successfully!")
print("Each tool call response will now have a globally unique ID.")
