#!/usr/bin/env node
/**
 * Raw MCP debug script - see exactly what SQLcl sends back
 */
const { spawn } = require('child_process');

const SQLCL_PATH = '/Users/ashukum/sqlcl/sqlcl/bin/sql';

const proc = spawn(SQLCL_PATH, ['-mcp'], { stdio: ['pipe', 'pipe', 'pipe'] });

proc.stderr.on('data', (d) => console.error('[stderr]', d.toString()));

// Collect raw stdout bytes
proc.stdout.on('data', (chunk) => {
  const raw = chunk.toString();
  console.log('[stdout raw bytes]', JSON.stringify(raw));
});

proc.on('exit', (code) => console.log('exited', code));

// Wait 4s then send initialize
setTimeout(() => {
  const msg = {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'test', version: '1.0.0' },
    },
  };
  const json = JSON.stringify(msg);
  const frame = `Content-Length: ${Buffer.byteLength(json)}\r\n\r\n${json}`;
  console.log('[sending]', frame);
  proc.stdin.write(frame);
}, 4000);

// Kill after 15s
setTimeout(() => {
  console.log('Timeout - killing');
  proc.kill();
  process.exit(0);
}, 15000);
