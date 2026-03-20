#!/usr/bin/env python3
"""
Patch OCI GenAI transformation to use fake streaming.

When LibreChat's ChatOpenAI sends stream:true to LiteLLM, LiteLLM tries to
stream from OCI GenAI. But OCI GenAI's streaming is broken/unsupported for
this model, causing "Error building chunks for logging/streaming usage
calculation".

The fix: Override should_fake_stream() to return True. This makes LiteLLM
call the non-streaming OCI API and then convert the response into SSE chunks
for the client. The client (LibreChat) gets a proper streamed response
without OCI needing to actually support streaming.
"""

TRANSFORM_FILE = "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"

with open(TRANSFORM_FILE, "r") as f:
    content = f.read()

# Check if already patched
if "def should_fake_stream" in content:
    print("Already patched - should_fake_stream override exists.")
    exit(0)

# Find the sign_request method and insert should_fake_stream before it
old = "    def sign_request("

new = """    def should_fake_stream(
        self,
        model: Optional[str],
        stream: Optional[bool],
        custom_llm_provider: Optional[str] = None,
    ) -> bool:
        \"\"\"
        PATCH: Always fake stream for OCI GenAI.
        OCI GenAI streaming is broken/unsupported for tool-calling models.
        This makes LiteLLM call the non-streaming API and convert the
        response to SSE chunks for the client.
        \"\"\"
        return True

    def sign_request("""

content = content.replace(old, new, 1)

with open(TRANSFORM_FILE, "w") as f:
    f.write(content)

print("Patched: should_fake_stream now returns True for OCI GenAI.")
print("Restart LiteLLM for changes to take effect.")
