#!/usr/bin/env python3
"""Fix corrupted response logging in OCI transformation."""

TRANSFORM_FILE = "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"

with open(TRANSFORM_FILE, "r") as f:
    lines = f.readlines()

# Find and replace the corrupted block
new_lines = []
skip_until_return = False
i = 0
while i < len(lines):
    line = lines[i]
    
    # Detect start of the corrupted logging block
    if "# PATCH: Log response details for debugging" in line:
        # Skip everything until "return model_response"
        while i < len(lines):
            if lines[i].strip() == "return model_response":
                # Write clean logging block + return
                new_lines.append("        # PATCH: Log response details for debugging\n")
                new_lines.append("        try:\n")
                new_lines.append('            _dl.debug("=== transform_response ===")\n')
                new_lines.append("            _choice = model_response.choices[0] if model_response.choices else None\n")
                new_lines.append("            if _choice:\n")
                new_lines.append('                _fr = getattr(_choice, "finish_reason", "N/A")\n')
                new_lines.append('                _msg = getattr(_choice, "message", None)\n')
                new_lines.append('                _has_tc = bool(getattr(_msg, "tool_calls", None)) if _msg else False\n')
                new_lines.append('                _dl.debug("  finish_reason=%s has_tool_calls=%s" % (_fr, _has_tc))\n')
                new_lines.append('            _dl.debug("=== end response ===")\n')
                new_lines.append("        except Exception:\n")
                new_lines.append("            pass\n")
                new_lines.append("\n")
                new_lines.append("        return model_response\n")
                i += 1
                break
            i += 1
        continue
    
    new_lines.append(line)
    i += 1

with open(TRANSFORM_FILE, "w") as f:
    f.writelines(new_lines)

print("Fixed corrupted response logging.")
