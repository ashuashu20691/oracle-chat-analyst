#!/usr/bin/env node
/**
 * Dump the full tool schemas from SQLcl MCP server
 */
const { Client } = require(
  '../LibreChat/node_modules/@modelcontextprotocol/sdk/dist/cjs/client/index.js'
);
const { StdioClientTransport } = require(
  '../LibreChat/node_modules/@modelcontextprotocol/sdk/dist/cjs/client/stdio.js'
);

const SQLCL_PATH = '/Users/ashukum/sqlcl/sqlcl/bin/sql';

async function main() {
  const transport = new StdioClientTransport({
    command: SQLCL_PATH,
    args: ['-mcp'],
  });
  const client = new Client({ name: 'schema-dump', version: '1.0.0' });
  
  await client.connect(transport);
  const { tools } = await client.listTools();
  
  for (const tool of tools) {
    console.log('\n' + '='.repeat(50));
    console.log(`Tool: ${tool.name}`);
    console.log(`Description: ${tool.description}`);
    console.log('Input Schema:');
    console.log(JSON.stringify(tool.inputSchema, null, 2));
  }
  
  await client.close();
  process.exit(0);
}

main().catch((e) => { console.error(e); process.exit(1); });
