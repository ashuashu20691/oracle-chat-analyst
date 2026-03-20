#!/usr/bin/env python3
"""Fix the corrupted debug logging in transform_request and ensure tool_id patch is intact."""

import os

tf = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

with open(tf, 'r') as f:
    content = f.read()

# Find and replace the corrupted debug block
corrupted = """        # DEBUG: Log incoming messages to understand tool call flow
        import logging
        _debug_logger = logging.getLogger("litellm.oci.debug_transform")
        _debug_logger.setLevel(logging.DEBUG)
        if not _debug_logger.handlers:
            _fh = logging.FileHandler("/Users/ashukum/libre-chat-custom-desktop/logs/oci_messages_debug.log")
            _fh.set            _fh.set            _fh.set         addHandler(_fh)
        _debug_logger.debug("=== transform_request called ===")
        for _idx, _msg in enumerate(messages):
            _role = _msg.get("role", "?")
            _tc = _msg.get("tool_calls")
            _tcid = _msg.get("tool_call_id")
            _content = str(_msg.get("content", ""))[:200]
            _debug_logger.debug(f"  [{_idx}] role={_role} tool_call_id={_tcid} has_tool_calls={bool(_tc)} content={_content}")
            if _tc:
                for _t in _tc:
                    if isinstance(_t, dict):
                        _debug_logger.debug(f"       tc: id={_t.get('id')} func={_t.get('function',{}).get('name')}")
        _debug_logger.debug("=== end messages ===")

        oci_compartment_id"""

fixed = """        # DEBUG: Log incoming messages
        import logging as _dbg_log
        _dl = _dbg_log.getLogger("litellm.oci.debug")
        _dl.setLevel(_dbg_log.DEBUG)
        if not _dl.handlers:
            _fh = _dbg_log.FileHandler("/Users/ashukum/libre-chat-custom-desktop/logs/oci_messages_debug.log")
            _fh.setLevel(_dbg_log.DEBUG)
            _dl.addHandler(_fh)
        _dl.debug("=== transform_request ===")
        for _i, _m in enumerate(messages):
            _r = _m.get("role", "?")
            _tc = _m.get("tool_calls")
            _tid = _m.get("tool_call_id")
            _c = str(_m.get("content", ""))[:200]
            _dl.debug("  [%d] role=%s tool_call_id=%s has_tool_calls=%s content=%s" % (_i, _r, _tid, bool(_tc), _c))
            if _tc and isinstance(_tc, list):
                for _t in _tc:
                    if isinstance(_t, dict):
                        _dl.debug("       tc: id=%s func=%s" % (_t.get("id"), _t.get("function", {}).get("name")))
        _dl.debug("=== end ===")

        oci_compartment_id"""

if corrupted in content:
    content = content.replace(corrupted, fixed)
    with open(tf, 'w') as f:
        f.write(content)
    print("OK: Fixed corrupted debug logging")
else:
    print("FAIL: Could not find corrupted pattern")
    # Try to show what's there
    idx = content.find("def transform_request(")
    if idx >= 0:
        print("Found transform_request at position", idx)
        print(repr(content[idx:idx+500]))
