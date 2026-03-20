#!/usr/bin/env node
/**
 * Connects to SQLcl MCP server via stdio and fetches tool schemas.
 */
const { spawn } = require('child_process');

const SQLCL_PATH = '/Users/ashukum/sqlcl/sqlcl/bin/sql';

const child = spawn(SQLCL_PATH, ['-mcp'], {
  stdio: ['pipe', 'pipe', 'pipe'],
});

let buffer = '';

child.stdout.on('data', (data) => {
  buffer += data.toString();
  // Try to parse complete JSON-RPC messages
  const lines = buffer.split('\n');
  buffer = lines.pop(); // keep incomplete line
  for (const line of lines) {
    if (line.trim()) {
      try {
        const msg = JSON.parse(line.trim());
        if (msg.id === 0) {
          // Initialize response, send initialized notification + tools/list
          child.stdin.write(JSON.stringify({jsonrpc:"2.0",method:"notifications/initialized"}) + '\n');
          child.stdin.write(JSON.stringify({jsonrpc:"2.0",id:2,method:"tools/list",params:{}}) + '\n');
        } else if (msg.id === 2) {
          // Tools list response
          console.log(JSON.stringify(msg.result, null, 2));
          child.kill();
          process.exit(0);
        }
      } catch(e) {
        // not valid JSON, skip
      }
    }
  }
});

child.stderr.on('data', (data) => {
  // ignore stderr
});

// Send initialize
child.stdin.write(JSON.stringify({
  jsonrpc: "2.0",
  id: 0,
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "test-client", version: "1.0.0" }
  }
}) + '\n');

setTimeout(() => {
  console.error('Timeout waiting for tools/list response');
  child.kill();
  process.exit(1);
}, 15000);
