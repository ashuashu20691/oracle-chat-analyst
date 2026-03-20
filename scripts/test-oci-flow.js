#!/usr/bin/env node
/**
 * Test the exact OCI GenAI flow through LiteLLM proxy.
 * Simulates the LangGraph agent loop to identify where tool responses get lost.
 */

const LITELLM_URL = 'http://localhost:4000/chat/completions';

async function callLLM(messages, tools) {
  const body = {
    model: 'oci-genai',
    messages,
    stream: false,
  };
  if (tools && tools.length > 0) {
    body.tools = tools;
  }

  console.log(`\n=== Calling LLM with ${messages.length} messages ===`);
  for (const [i, m] of messages.entries()) {
    const tc = m.tool_calls ? ` tool_calls=[${m.tool_calls.map(t => t.id).join(',')}]` : '';
    const tcid = m.tool_call_id ? ` tool_call_id=${m.tool_call_id}` : '';
    const content = m.content ? m.content.substring(0, 80) : '(none)';
    console.log(`  [${i}] ${m.role}${tc}${tcid}: ${content}`);
  }

  const resp = await fetch(LITELLM_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const text = await resp.text();
    console.error(`ERROR ${resp.status}: ${text.substring(0, 500)}`);
    return null;
  }

  const data = await resp.json();
  const choice = data.choices?.[0];
  const msg = choice?.message;

  console.log(`\n  Response: finish_reason=${choice?.finish_reason}`);
  if (msg?.tool_calls) {
    for (const tc of msg.tool_calls) {
      console.log(`  Tool call: id=${tc.id} func=${tc.function?.name} args=${tc.function?.arguments?.substring(0, 100)}`);
    }
  }
  if (msg?.content) {
    console.log(`  Content: ${msg.content.substring(0, 200)}`);
  }

  return msg;
}

const tools = [
  {
    type: 'function',
    function: {
      name: 'connect_mcp_SQLcl_conn1',
      description: 'Connect to a database',
      parameters: {
        type: 'object',
        properties: {
          connection_name: { type: 'string' },
          mcp_client: { type: 'string' },
          model: { type: 'string' },
        },
        required: ['connection_name', 'mcp_client', 'model'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'run-sql_mcp_SQLcl_conn1',
      description: 'Run a SQL query',
      parameters: {
        type: 'object',
        properties: {
          sql: { type: 'string' },
          mcp_client: { type: 'string' },
          model: { type: 'string' },
        },
        required: ['sql', 'mcp_client', 'model'],
      },
    },
  },
];

async function main() {
  console.log('=== Testing OCI GenAI Tool Call Flow ===\n');

  // Step 1: Initial call - should get a tool_call for connect
  const messages1 = [
    { role: 'system', content: 'You are a database assistant. Connect to BASE_DB_23AI when asked.' },
    { role: 'user', content: 'Connect to the database BASE_DB_23AI' },
  ];

  const resp1 = await callLLM(messages1, tools);
  if (!resp1?.tool_calls) {
    console.log('\nNo tool call returned. Test cannot continue.');
    return;
  }

  const tc1 = resp1.tool_calls[0];
  console.log(`\n--- Simulating tool execution for ${tc1.function.name} ---`);

  // Step 2: Add tool response and call again
  const messages2 = [
    ...messages1,
    { role: 'assistant', content: null, tool_calls: resp1.tool_calls },
    { role: 'tool', tool_call_id: tc1.id, content: 'Connected successfully to BASE_DB_23AI. Oracle Database 23ai.' },
  ];

  const resp2 = await callLLM(messages2, tools);
  if (!resp2) {
    console.log('\nLLM call failed after tool response.');
    return;
  }

  console.log('\n--- Step 2 complete ---');
  console.log(`Response has tool_calls: ${!!resp2.tool_calls}`);
  console.log(`Response content: ${resp2.content?.substring(0, 200)}`);

  // Step 3: User asks for DBA users
  const messages3 = [
    ...messages2,
    { role: 'assistant', content: resp2.content || 'Connected to the database.' },
    { role: 'user', content: 'List all users with DBA role' },
  ];

  const resp3 = await callLLM(messages3, tools);
  if (!resp3?.tool_calls) {
    console.log('\nNo tool call for SQL query. Unexpected.');
    return;
  }

  const tc3 = resp3.tool_calls[0];
  console.log(`\n--- Simulating SQL execution for ${tc3.function.name} ---`);

  // Step 4: Add SQL result and call again
  const messages4 = [
    ...messages3,
    { role: 'assistant', content: null, tool_calls: resp3.tool_calls },
    { role: 'tool', tool_call_id: tc3.id, content: '"GRANTEE"\n"SYS"\n"SYSTEM"\n"ADMIN"' },
  ];

  const resp4 = await callLLM(messages4, tools);
  if (!resp4) {
    console.log('\nLLM call failed after SQL result.');
    return;
  }

  console.log('\n=== FINAL RESULT ===');
  console.log(resp4.content);
  console.log('\n✓ Full tool call flow completed successfully!');
}

main().catch(console.error);
