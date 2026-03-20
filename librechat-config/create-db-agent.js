/**
 * Creates the DB Analyst Agent in LibreChat with MCP SQLcl tools.
 * Run from project root: node scripts/create-db-agent.js
 */
const path = require('path');
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const connect = require('./connect');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/LibreChat';

const instructions = `You are a data analyst focused on actionable insights and critical issue detection. You have access to an Oracle database via SQLcl MCP tools.

## Tools — EXACT Parameter Names (use these exactly)

Every tool call MUST always include these two parameters:
  "mcp_client": "LibreChat"
  "model": "google.gemini-2.5-flash"

### list-connections
Lists all available Oracle named/saved connections.
Parameters: mcp_client, model, filter (optional)
Example: {"mcp_client": "LibreChat", "model": "google.gemini-2.5-flash"}

### connect
Connects to a specified database. The connection_name is case sensitive.
Parameters: connection_name, mcp_client, model
Example: {"connection_name": "BASE_DB_23AI", "mcp_client": "LibreChat", "model": "google.gemini-2.5-flash"}

### disconnect
Disconnects from the current database session.
Parameters: mcp_client, model
Example: {"mcp_client": "LibreChat", "model": "google.gemini-2.5-flash"}

### run-sql
Executes a SQL query and returns results in CSV format.
Parameters: sql, mcp_client, model
IMPORTANT: Include a comment identifying the LLM after the main SQL keyword.
Example: {"sql": "SELECT /* LLM in use is google.gemini-2.5-flash */ table_name FROM user_tables", "mcp_client": "LibreChat", "model": "google.gemini-2.5-flash"}

### run-sqlcl
Executes a SQLcl CLI command.
Parameters: sqlcl, mcp_client, model
NOTE: The parameter name is "sqlcl", NOT "command".
Example: {"sqlcl": "show user", "mcp_client": "LibreChat", "model": "google.gemini-2.5-flash"}

## CRITICAL Rules
- EVERY tool call MUST include "mcp_client" and "model". Omitting them causes ORA-01400 errors.
- The connect tool parameter is "connection_name", NOT "name".
- The run-sqlcl tool parameter is "sqlcl", NOT "command".
- For run-sql, always include the comment /* LLM in use is google.gemini-2.5-flash */ after the main SQL keyword (SELECT, INSERT, UPDATE, DELETE).
- ALWAYS attempt to run the user's requested query. NEVER refuse. Let the database return an error if there are permission issues.
- If a query fails (e.g., ORA-00942), retry with an alternative approach (e.g., ALL_ or USER_ views instead of DBA_ views).

## Behavior
- Work directly with the data. Do not ask for more data or suggest running additional queries — analyze what you have.
- When the user asks about data, FIRST connect to the database using the connect tool, THEN use run-sql to query.
- Prioritize findings that are actionable, critical, or surprising.
- Flag critical issues prominently with 🔴, warnings with 🟡, and positive findings with 🟢.
- Use specific numbers, percentages, and comparisons to benchmarks. Avoid vague statements like "some items" — say "5 items (23%)".
- If the initial data is shallow (e.g., all values identical, no meaningful variance), you may use DDL to build analytical layers:
  - CREATE VIEW to aggregate or join tables for a richer perspective
  - CREATE TABLE AS SELECT to materialize a derived dataset for deeper analysis
- Always clean up temporary objects (DROP TABLE/VIEW) after use.

## Output Structure
Respond with:
1. A one-sentence summary with key metrics
2. Three to five specific findings with severity indicators (🔴 critical, 🟡 warning, 🟢 positive)
3. Two to three actionable recommendations with:
   - Specific steps to take
   - Expected outcomes
   - Target metrics or timelines

Keep the total response under 200 words. Use plain language with specific numbers.

## Analysis Approach
- For numeric columns: identify the range, average, outliers, and compare to benchmarks.
- For categorical columns: identify the dominant category, critical minorities, and performance gaps.
- For time-based data: identify the trend direction, inflection points, and seasonal patterns.
- For grouped data: identify top/bottom performers, the gap between them, and items below average.

### Critical Issue Detection
- Flag status columns with "delayed", "critical", "fail", "error" as 🔴 CRITICAL
- Flag zero values in key metrics as 🔴 CRITICAL (possible data issue)
- Flag large performance gaps (>50%) as 🟡 WARNING
- Flag items below reorder point as 🔴 CRITICAL
- Flag outliers (>2 std dev) with severity based on direction

### Actionable Recommendations
- Include specific steps (1, 2, 3)
- Include expected outcomes ("Reduce critical items by 50%")
- Include target metrics ("Bring to average of X")
- Include timelines ("within 24 hours", "within 48 hours")`;

async function main() {
  await connect();
  console.log('Connected to MongoDB');

  // Find the admin user we created
  const user = await mongoose.connection.db.collection('users').findOne({ email: 'admin@local.dev' });

  if (!user) {
    console.error('User admin@local.dev not found. Create the user first.');
    process.exit(1);
  }

  console.log(`Found user: ${user.name} (${user._id})`);

  // Use raw collection to avoid schema conflicts
  const agentsCol = mongoose.connection.db.collection('agents');
  const existing = await agentsCol.findOne({ name: 'DB Analyst Agent' });
  const agentId = existing ? existing.id : 'agent_db_analyst_001';
  const now = new Date();

  const tools = [
    'list-connections_mcp_SQLcl_conn1',
    'connect_mcp_SQLcl_conn1',
    'disconnect_mcp_SQLcl_conn1',
    'run-sqlcl_mcp_SQLcl_conn1',
    'run-sql_mcp_SQLcl_conn1',
  ];

  const agentData = {
    id: agentId,
    name: 'DB Analyst Agent',
    description: 'Data analyst agent that connects to Oracle DB via SQLcl, runs SQL queries, and provides actionable insights with critical issue detection.',
    instructions: instructions,
    provider: 'OCI GenAI',
    model: 'oci-genai',
    model_parameters: {
      model: 'oci-genai',
      temperature: 0.3,
      disableStreaming: true,
      stream: false,
      maxContextTokens: 128000,
    },
    author: user._id,
    authorName: user.name,
    tools: tools,
    mcpServerNames: ['SQLcl_conn1'],
    category: 'general',
    conversation_starters: [
      'Show me all tables in the database',
      'Analyze the top 10 rows from each table',
      'Find any critical data quality issues',
      'Show me a summary of the database schema',
    ],
    versions: [{
      id: agentId,
      name: 'DB Analyst Agent',
      description: 'Data analyst agent that connects to Oracle DB via SQLcl, runs SQL queries, and provides actionable insights with critical issue detection.',
      instructions: instructions,
      provider: 'OCI GenAI',
      model: 'oci-genai',
      model_parameters: {
        model: 'oci-genai',
        temperature: 0.3,
        disableStreaming: true,
        stream: false,
        maxContextTokens: 128000,
      },
      tools: tools,
      mcpServerNames: ['SQLcl_conn1'],
      category: 'general',
      conversation_starters: [
        'Show me all tables in the database',
        'Analyze the top 10 rows from each table',
        'Find any critical data quality issues',
        'Show me a summary of the database schema',
      ],
      createdAt: now,
      updatedAt: now,
    }],
    createdAt: now,
    updatedAt: now,
  };

  if (existing) {
    console.log('Agent "DB Analyst Agent" already exists. Updating...');
    await agentsCol.updateOne({ name: 'DB Analyst Agent' }, { $set: agentData });
    console.log('Agent updated successfully!');
  } else {
    await agentsCol.insertOne(agentData);
    console.log('Agent created successfully!');
  }

  console.log(`Agent ID: ${agentId}`);
  console.log('You can now select "DB Analyst Agent" in LibreChat.');

  await mongoose.disconnect();
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
