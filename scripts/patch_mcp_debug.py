#!/usr/bin/env python3
"""Replace console.log MCP debug with file-based logging."""

FILE = "LibreChat/packages/api/dist/index.js"

with open(FILE, "r") as f:
    content = f.read()

# Find and replace the debug block
old = '// DEBUG: Log raw MCP tool result before formatting'
new_block = '// DEBUG: Log raw MCP tool result to file'

if old in content:
    # Find the try block start
    idx = content.index(old)
    # Find the matching catch block end - look for the next "catch (error)" after our try
    # We need to replace from "// DEBUG:" to just before the outer "catch (error)"
    
    # Find "return formatted;" or "return formatToolContent" after our marker
    # Actually, let's just replace the console.log calls with file writes
    content = content.replace(
        'console.log(`[MCP_DEBUG][${toolName}] raw result.content: ${_rc}`)',
        'require("fs").appendFileSync("/Users/ashukum/libre-chat-custom-desktop/logs/mcp_tool_debug.log", `[${new Date().toISOString()}][${toolName}] provider=${provider} raw=${_rc}\\n`)'
    )
    content = content.replace(
        'console.log(`[MCP_DEBUG][${toolName}] provider: ${provider}`)',
        '/* provider logged above */'
    )
    content = content.replace(
        'console.log(`[MCP_DEBUG][${toolName}] formatted[0]',
        'require("fs").appendFileSync("/Users/ashukum/libre-chat-custom-desktop/logs/mcp_tool_debug.log", `  formatted: type=${typeof formatted[0]} len=${String(formatted[0]).length} val=${String(formatted[0]).substring(0, 500)}\\n`); /* was console.log(`[MCP_DEBUG][${toolName}] formatted[0]'
    )
    content = content.replace(
        'console.log(`[MCP_DEBUG][${toolName}] format error`, e)',
        'require("fs").appendFileSync("/Users/ashukum/libre-chat-custom-desktop/logs/mcp_tool_debug.log", `[ERROR][${toolName}] ${e.message}\\n`)'
    )
    
    with open(FILE, "w") as f:
        f.write(content)
    print("Patched MCP debug logging to write to file.")
else:
    print("Debug marker not found - may already be patched or removed.")
