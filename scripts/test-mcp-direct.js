#!/usr/bin/env node
/**
 * Direct MCP Tool Test Script
 * 
 * Uses the @modelcontextprotocol/sdk (same as LibreChat) to talk
 * to SQLcl MCP server via stdio. Bypasses LiteLLM/LLM entirely.
 *
 * Test flow:
 *   1. Connect to BASE_DB_23AI
 *   2. Run SQL: List all users with DBA role and last login time
 *   3. Print results
 *   4. Disconnect
 */

const { Client } = require(
  '../LibreChat/node_modules/@modelcontextprotocol/sdk/dist/cjs/client/index.js'
);
const { StdioClientTransport } = require(
  '../LibreChat/node_modules/@modelcontextprotocol/sdk/dist/cjs/client/stdio.js'
);

const SQLCL_PATH = process.env.SQLCL_PATH || '/Users/ashukum/sqlcl/sqlcl/bin/sql';
const CONNECTION_NAME = 'BASE_DB_23AI';
const MODEL_NAME = 'oci-genai/gemini-2.5-flash';
const MCP_CLIENT = 'kiro-test-script';

const SQL_QUERY = `SELECT /* LLM in use is ${MODEL_NAME} */
    u.USERNAME,
    u.ACCOUNT_STATUS,
    u.CREATED,
    u.LAST_LOGIN,
    r.GRANTED_ROLE,
    r.ADMIN_OPTION
FROM DBA_USERS u
JOIN DBA_ROLE_PRIVS r ON u.USERNAME = r.GRANTEE
WHERE r.GRANTED_ROLE = 'DBA'
ORDER BY u.USERNAME`;

async function main() {
  console.log('='.repeat(60));
  console.log('SQLcl MCP Direct Test');
  console.log('='.repeat(60));
  console.log(`SQLcl: ${SQLCL_PATH}`);
  console.log(`Connection: ${CONNECTION_NAME}\n`);

  const transport = new StdioClientTransport({
    command: SQLCL_PATH,
    args: ['-mcp'],
  });

  const client = new Client({ name: MCP_CLIENT, version: '1.0.0' });

  try {
    console.log('Connecting to MCP server...');
    await client.connect(transport);
    console.log('Connected.\n');

    // Step 1: Connect to database
    console.log('--- Step 1: Connect to BASE_DB_23AI ---');
    const connectResult = await client.callTool({
      name: 'connect',
      arguments: {
        connection_name: CONNECTION_NAME,
        model: MODEL_NAME,
        mcp_client: MCP_CLIENT,
      },
    });
    printResult(connectResult);

    // Step 2: Run the query
    console.log('\n--- Step 2: Run SQL Query ---');
    console.log(`SQL:\n${SQL_QUERY}\n`);
    const queryResult = await client.callTool({
      name: 'run-sql',
      arguments: {
        sql: SQL_QUERY,
        model: MODEL_NAME,
        mcp_client: MCP_CLIENT,
      },
    });
    printResult(queryResult);

    // Step 3: Disconnect
    console.log('\n--- Step 3: Disconnect ---');
    const disconnectResult = await client.callTool({
      name: 'disconnect',
      arguments: {
        model: MODEL_NAME,
        mcp_client: MCP_CLIENT,
      },
    });
    printResult(disconnectResult);

    console.log('\n' + '='.repeat(60));
    console.log('TEST PASSED');
    console.log('='.repeat(60));
  } catch (err) {
    console.error('\nTEST FAILED:', err.message);
    if (err.code) console.error('Error code:', err.code);
  } finally {
    try { await client.close(); } catch (_) {}
    process.exit(0);
  }
}

function printResult(result) {
  if (!result || !result.content) {
    console.log('  (no content)');
    return;
  }
  for (const item of result.content) {
    if (item.text) {
      console.log(item.text);
    } else {
      console.log(JSON.stringify(item, null, 2));
    }
  }
}

main();
