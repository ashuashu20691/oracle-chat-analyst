# LibreChat SQL Explorer Agent Setup Guide

## Step 1: Access the Agent Creation Interface

1. Open http://localhost:3080 in your browser
2. Log in with your credentials:
   - Email: ashu.kumar@oracle.com
   - Password: Igdefault@123
3. Click on the "My Agents" tab in the left sidebar

## Step 2: Create a New Agent

1. Click the "Create Agent" or "+" button
2. Fill in the agent details:

### Basic Information
- **Name**: SQL Explorer Agent
- **Description**: AI assistant for exploring Oracle databases with natural language

### Model Configuration
- **Provider**: Select "OCI GenAI"
- **Model**: oci-genai

### Tools/MCP Servers
- Enable the **SQLcl_conn1** MCP server
- This will give the agent access to these tools:
  - `list-connections`: List available database connections
  - `connect`: Connect to a database
  - `disconnect`: Disconnect from database
  - `run-sqlcl`: Execute SQLcl commands
  - `run-sql`: Execute SQL queries

### Agent Instructions (System Prompt)

Copy and paste this into the instructions field:

```
You are an AI data exploration assistant with direct access to an Oracle database through SQLcl MCP tools.

## Available Tools

- list-connections: List available database connections
- connect: Connect to a database
- disconnect: Close database connection
- run-sql: Execute SQL queries
- run-sqlcl: Execute SQLcl commands

## Your Workflow

1. **Connect to Database**: Use the connect tool first if not already connected
2. **Explore Schema**: Use run-sql to query system tables (USER_TABLES, USER_TAB_COLUMNS)
3. **Execute Queries**: Run SQL queries based on user requests
4. **Present Results**: Format results clearly for the user

## SQL Best Practices

- Use Oracle SQL syntax
- Always use table aliases for clarity
- Include appropriate WHERE clauses
- Use ORDER BY for sorted results
- Limit large result sets with FETCH FIRST n ROWS ONLY
- Format dates with TO_CHAR when needed

## Error Handling

When you encounter SQL errors:
1. Analyze the error message
2. Check table and column names using system tables
3. Correct the query and retry
4. Explain what was wrong and how you fixed it

## Important Rules

- NEVER execute DROP, DELETE, TRUNCATE, or other destructive SQL
- ALWAYS explain your reasoning before executing queries
- Provide helpful context with your results
```

## Step 3: Save and Use the Agent

1. Click "Save" or "Create" to save your agent
2. The agent will appear in your "My Agents" list
3. Click on the agent to start a conversation
4. You can now ask questions like:
   - "What tables are available in the database?"
   - "Show me the schema of the EMPLOYEES table"
   - "Query the top 10 customers by revenue"

## Troubleshooting

### If you still see "agent_id is required" error:
- Make sure you're using the agent you created, not the regular chat
- The agent should be selected from the "My Agents" tab

### If MCP tools aren't available:
- Check that SQLcl_conn1 is enabled in the agent configuration
- Verify the backend logs show MCP server initialized successfully

### If database connection fails:
- Ensure your Oracle database is running and accessible
- Check that SQLcl is properly configured with connection details
- You may need to use the `connect` tool with proper credentials

## Next Steps

Once your agent is working:
1. Test basic SQL queries
2. Explore your database schema
3. Try more complex queries with joins and aggregations
4. The agent will automatically handle errors and retry with corrections
