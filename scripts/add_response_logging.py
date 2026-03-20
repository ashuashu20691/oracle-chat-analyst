#!/usr/bin/env python3
"""Add response debug logging to transform_response in OCI transformation."""

TRANSFORM_FILE = "/Users/ashukum/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"

with open(TRANSFORM_FILE, "r") as f:
    content = f.read()

old = '''        model_response._hidden_params["additional_headers"] = raw_response.headers

        return model_response'''

new = '''        model_response._hidden_params["additional_headers"] = raw_response.headers

        # PATCH: Log response details for debugging
        try:
            _dl.debug("=== transform_response ===")
            _choice = model_response.choices[0] if model_response.choices else None
            if _choice:
                _fr = getattr(_choice, "finish_reason", "N/A")
                _msg = getattr(_choice, "message", None)
                _has_tc = bool(getattr(_msg, "tool_calls", None)) if _msg else False
                _cont = getattr(_msg, "content", "")
                if _cont and len(str(_cont)) > 100:
                    _cont = str(_cont)[:100] + "..."
                _dl.debug("  finish_reason=%s has_tool_calls=%s content=%s" % (_fr, _has_tc, _cont))
                if _has_tc:
                    for _t in _msg.tool_calls:
                        _dl.debug("    tool_call: id=%s func=%s" % (getattr(_t, "id", "?"), getattr(getattr(_t, "function", None), "name", "?")))
            _dl.debug("=== end response ===")
        except Exception:
            pass

        return model_response'''

if old in content:
    content = content.replace(old, new)
    with open(TRANSFORM_FILE, "w") as f:
        f.write(content)
    print("Response logging added.")
elif "=== transform_response ===" in content:
    print("Already patched.")
else:
    print("ERROR: target not found")
