#!/usr/bin/env python3
"""Add debug logging to LiteLLM OCI transform_request to capture messages from LibreChat."""

import os

transformation_file = os.path.expanduser(
    "~/.local/pipx/venvs/litellm/lib/python3.12/site-packages/litellm/llms/oci/chat/transformation.py"
)

with open(transformation_file, 'r') as f:
    content = f.read()

old = '''    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        litellm_params: dict,
        headers: dict,
    ) -> dict:
        oci_compartment_id = optional_params.get("oci_compartment_id", None)'''

debug_code = '''    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        litellm_params: dict,
        headers: dict,
    ) -> dict:
        # DEBUG: Log incoming messages
        import logging as _logging
        _dl = _logging.getLogger("litellm.oci.debug")
        _dl.setLevel(_logging.DEBUG)
        if not _dl.handlers:
            _fh = _logging.FileHandler("/Users/ashukum/libre-chat-custom-desktop/logs/oci_messages_debug.log")
            _fh.setLevel(_logging.DEBUG)
            _dl.addHandler(_fh)
        _dl.debug("=== transform_request ===")
        for _i, _m in enumerate(messages):
            _r = _m.get("role", "?")
            _tc = _m.get("tool_calls")
            _tid = _m.get("tool_call_id")
            _c = str(_m.get("content", ""))[:200]
            _dl.debug(f"  [{_i}] role={_r} tool_call_id={_tid} has_tool_calls={bool(_tc)} content={_c}")
            if _tc:
                for _t in (_tc if isinstance(_tc, list) else []):
                    if isinstance(_t, dict):
                        _dl.debug(f"       tc: id={_t.get('id')} func={_t.get('function',{}).get('name')}")
        _dl.debug("=== end ===")

        oci_compartment_id = optional_params.get("oci_compartment_id", None)'''

if old in content:
    content = content.replace(old, debug_code)
    with open(transformation_file, 'w') as f:
        f.write(content)
    print("OK: Debug logging added to transform_request")
else:
    print("FAIL: Could not find transform_request pattern")
    print("Checking if already patched...")
    if "DEBUG: Log incoming messages" in content:
        print("Already has debug logging")
    else:
        print("Pattern mismatch - check file manually")
