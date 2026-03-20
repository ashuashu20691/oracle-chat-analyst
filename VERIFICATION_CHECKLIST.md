# LibreChat OCI SQL Explorer - Verification Checklist

This comprehensive checklist verifies that all configurations are valid, services can start successfully, and the end-to-end flow works correctly.

**Task 7 Requirements**: 10.2, 10.3, 10.4, 10.5, 17.2, 17.3

---

## Pre-Verification Setup

### Environment Preparation

- [ ] **1.1** `.env` file exists and contains all required variables
- [ ] **1.2** `LITELLM_MASTER_KEY` is set and is a strong random key
- [ ] **1.3** `DB_CONNECTION_STRING` is properly formatted
- [ ] **1.4** `DB_WALLET_PATH` is set (if using Autonomous Database)
- [ ] **1.5** OCI configuration exists at `~/.oci/config`
- [ ] **1.6** All scripts have execute permissions (`chmod +x scripts/*.sh`)

### Configuration Files Validation

- [ ] **2.1** `litellm_config.yaml` exists in project root
- [ ] **2.2** `LibreChat/librechat.yaml` exists
- [ ] **2.3** `docker-compose.yml` exists (for Docker deployment)
- [ ] **2.4** HTML artifact templates exist in `.kiro/specs/librechat-oci-sql-explorer/templates/`

---

## Phase 1: Configuration Validation

### LiteLLM Configuration (litellm_config.yaml)


**Requirement 17.1**: LibreChat SHALL validate the librechat.yaml syntax

- [ ] **3.1** File contains `model_list` section
- [ ] **3.2** Model name is set to `oci-genai` or similar
- [ ] **3.3** `litellm_params.model` starts with `oci/` (e.g., `oci/cohere.command-r-plus`)
- [ ] **3.4** `api_base` points to valid OCI GenAI endpoint
- [ ] **3.5** `custom_llm_provider` is set to `oci`
- [ ] **3.6** `oci_config_path` points to `~/.oci/config` or credentials are provided
- [ ] **3.7** `general_settings.master_key` references `${LITELLM_MASTER_KEY}`
- [ ] **3.8** YAML syntax is valid (no parsing errors)

**Validation Command:**
```bash
python3 -c "import yaml; yaml.safe_load(open('litellm_config.yaml'))"
```

### LibreChat Configuration (LibreChat/librechat.yaml)

**Requirement 17.1**: LibreChat SHALL validate the librechat.yaml syntax

- [ ] **4.1** File contains `version: 1.1.0` or higher
- [ ] **4.2** `artifacts.enabled` is set to `true`
- [ ] **4.3** `artifacts.supportedTypes` includes `html` and `mermaid`
- [ ] **4.4** `endpoints.custom` section exists with LiteLLM configuration
- [ ] **4.5** Custom endpoint `baseURL` points to `http://localhost:4000`
- [ ] **4.6** Custom endpoint `apiKey` references `${LITELLM_MASTER_KEY}`
- [ ] **4.7** `agents` section contains "SQL Explorer Agent"
- [ ] **4.8** Agent has `instructions` field with system prompt
- [ ] **4.9** Agent has `tools` section with MCP configuration
- [ ] **4.10** MCP tool type is `mcp` with `streamable-http` transport
- [ ] **4.11** MCP tool URL points to `http://localhost:3100/mcp`
- [ ] **4.12** YAML syntax is valid (no parsing errors)

**Validation Command:**
```bash
python3 -c "import yaml; yaml.safe_load(open('LibreChat/librechat.yaml'))"
```


### Agent System Prompt Validation

**Requirement 9.1-9.4**: Agent configuration SHALL include proper system prompt

- [ ] **5.1** System prompt defines MCP tools (run_sql, list_tables, describe_table, disconnect)
- [ ] **5.2** System prompt includes reasoning transparency guidelines
- [ ] **5.3** System prompt includes autonomous error correction workflow
- [ ] **5.4** System prompt includes HTML artifact syntax examples
- [ ] **5.5** System prompt includes Chart.js CDN URL
- [ ] **5.6** System prompt includes bar chart template
- [ ] **5.7** System prompt includes line chart template
- [ ] **5.8** System prompt includes pie chart template
- [ ] **5.9** System prompt includes HTML table template
- [ ] **5.10** System prompt includes visualization selection logic

**Validation Method:**
```bash
grep -q "run_sql" LibreChat/librechat.yaml && echo "✓ MCP tools defined"
grep -q ":::artifact" LibreChat/librechat.yaml && echo "✓ Artifact syntax defined"
grep -q "Chart.js" LibreChat/librechat.yaml && echo "✓ Chart.js referenced"
```

---

## Phase 2: Service Startup Verification

### LiteLLM Startup

**Requirement 17.3**: LibreChat SHALL verify connectivity to OCI_GenAI through LiteLLM

- [ ] **6.1** LiteLLM starts without errors
- [ ] **6.2** LiteLLM binds to port 4000 (or configured port)
- [ ] **6.3** LiteLLM loads `litellm_config.yaml` successfully
- [ ] **6.4** LiteLLM authenticates with OCI GenAI
- [ ] **6.5** Health endpoint responds: `curl http://localhost:4000/health`
- [ ] **6.6** Model endpoint is accessible: `curl http://localhost:4000/models`
- [ ] **6.7** No authentication errors in logs
- [ ] **6.8** No configuration errors in logs

**Startup Command:**
```bash
source .env
./scripts/start-litellm.sh
```

**Expected Log Output:**
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:4000
```


**Health Check:**
```bash
curl http://localhost:4000/health
# Expected: {"status": "healthy"} or similar success response
```

**Test OCI GenAI Connection:**
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -d '{
    "model": "oci-genai",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
# Expected: JSON response with completion
```

### SQLcl MCP Server Startup

**Requirement 17.2**: LibreChat SHALL verify connectivity to SQLcl_MCP_Server

- [ ] **7.1** SQLcl MCP Server starts without errors
- [ ] **7.2** SQLcl MCP Server binds to port 3100 (or configured port)
- [ ] **7.3** Database connection is established successfully
- [ ] **7.4** Wallet is loaded (if using Autonomous Database)
- [ ] **7.5** Health endpoint responds: `curl http://localhost:3100/health`
- [ ] **7.6** MCP endpoint is accessible: `curl http://localhost:3100/mcp`
- [ ] **7.7** No database connection errors in logs
- [ ] **7.8** No authentication errors in logs

**Startup Command:**
```bash
source .env
./scripts/start-sqlcl-mcp.sh
```

**Expected Log Output:**
```
SQLcl MCP Server listening on http://localhost:3100
Database connection established
```

**Health Check:**
```bash
curl http://localhost:3100/health
# Expected: {"status": "healthy"} or similar success response
```


**Test Database Connection:**
```bash
# Test with list_tables tool (if MCP server provides test endpoint)
curl -X POST http://localhost:3100/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "list_tables",
      "arguments": {}
    },
    "id": 1
  }'
# Expected: JSON response with list of tables
```

### LibreChat Startup

**Requirement 10.2**: LibreChat SHALL initialize SQLcl_MCP_Server connection
**Requirement 10.5**: LibreChat SHALL provide startup status

- [ ] **8.1** LibreChat backend starts without errors
- [ ] **8.2** LibreChat frontend starts without errors
- [ ] **8.3** LibreChat validates `librechat.yaml` successfully
- [ ] **8.4** LibreChat initializes MCP server connection
- [ ] **8.5** LibreChat connects to LiteLLM proxy
- [ ] **8.6** MongoDB connection is established
- [ ] **8.7** Frontend is accessible at `http://localhost:3080`
- [ ] **8.8** Health endpoint responds: `curl http://localhost:3080/api/health`
- [ ] **8.9** No configuration errors in logs
- [ ] **8.10** No MCP initialization errors in logs

**Startup Command:**
```bash
source .env
./scripts/start-librechat.sh
```

**Expected Log Output:**
```
LibreChat backend starting...
Configuration validated successfully
MCP server initialized: oracle-sqlcl
Frontend available at: http://localhost:3080
```

**Health Check:**
```bash
curl http://localhost:3080/api/health
# Expected: {"status": "ok"} or similar success response
```


---

## Phase 3: End-to-End Flow Verification

### User Interface Verification

**Requirement 1.1-1.5**: LibreChat_Artifacts SHALL be enabled and functional

- [ ] **9.1** LibreChat UI loads successfully at `http://localhost:3080`
- [ ] **9.2** User can create account or log in
- [ ] **9.3** "SQL Explorer Agent" appears in agent dropdown
- [ ] **9.4** Chat interface is visible (left panel)
- [ ] **9.5** Artifact panel is available (right panel, when artifact is generated)
- [ ] **9.6** No JavaScript errors in browser console
- [ ] **9.7** No network errors in browser console

**Verification Steps:**
1. Open browser to `http://localhost:3080`
2. Create account or log in
3. Open browser developer tools (F12)
4. Check Console tab for errors
5. Check Network tab for failed requests

### Basic Query Test

**Requirement 10.3**: LibreChat SHALL verify SQLcl_MCP_Server connectivity by invoking list_tables

- [ ] **10.1** User can send message to SQL Explorer Agent
- [ ] **10.2** Agent responds to simple query: "Hello"
- [ ] **10.3** Agent can list tables: "Show me all tables"
- [ ] **10.4** Agent response includes table names
- [ ] **10.5** No error messages in agent response
- [ ] **10.6** Response time is reasonable (< 30 seconds)

**Test Query:**
```
Show me all tables in the database
```

**Expected Response:**
```
Let me check what tables are available...

I found the following tables:
- EMPLOYEES
- DEPARTMENTS
- PRODUCTS
- SALES
...
```


### Schema Discovery Test

**Requirement 7.1-7.5**: Agent SHALL discover database structure autonomously

- [ ] **11.1** Agent can describe table: "Describe the EMPLOYEES table"
- [ ] **11.2** Agent response includes column names
- [ ] **11.3** Agent response includes data types
- [ ] **11.4** Agent provides status update before querying schema
- [ ] **11.5** No errors in schema discovery

**Test Query:**
```
What columns are in the EMPLOYEES table?
```

**Expected Response:**
```
Let me check the schema for the EMPLOYEES table...

The EMPLOYEES table has the following columns:
- EMPLOYEE_ID (NUMBER) - Primary Key
- FIRST_NAME (VARCHAR2)
- LAST_NAME (VARCHAR2)
- EMAIL (VARCHAR2)
- HIRE_DATE (DATE)
- SALARY (NUMBER)
```

### SQL Query Execution Test

**Requirement 4.4**: SQLcl_MCP_Server SHALL execute operations against Oracle database

- [ ] **12.1** Agent can execute simple SELECT query
- [ ] **12.2** Query results are returned successfully
- [ ] **12.3** Agent provides status update before executing query
- [ ] **12.4** Results are formatted properly
- [ ] **12.5** No SQL execution errors

**Test Query:**
```
Show me the top 5 employees by salary
```

**Expected Response:**
```
Executing SQL query to retrieve the data...

Here are the top 5 employees by salary:
[Results displayed in table or artifact]
```


### HTML Artifact Generation Test

**Requirement 2.1-2.6**: Agent SHALL generate HTML artifacts with Chart.js

- [ ] **13.1** Agent generates artifact with `:::artifact` syntax
- [ ] **13.2** Artifact appears in right panel
- [ ] **13.3** Artifact type is `html`
- [ ] **13.4** Artifact has descriptive title
- [ ] **13.5** Both chat and artifact panels are visible simultaneously
- [ ] **13.6** Artifact content renders correctly

**Test Query:**
```
Show me a simple HTML table with employee data
```

**Expected Behavior:**
- Chat response appears in left panel
- HTML table artifact appears in right panel
- Table is styled and readable
- No rendering errors

### Bar Chart Visualization Test

**Requirement 8.1**: Agent SHALL generate bar charts for categorical + numeric data

- [ ] **14.1** Agent generates bar chart for appropriate data
- [ ] **14.2** Chart.js CDN is loaded successfully
- [ ] **14.3** Chart renders in artifact panel
- [ ] **14.4** Chart has axis labels
- [ ] **14.5** Chart has title
- [ ] **14.6** Chart is responsive
- [ ] **14.7** No JavaScript errors in console

**Test Query:**
```
Show me employee count by department as a bar chart
```

**Expected Behavior:**
- Agent generates `:::artifact type="html"` with Chart.js
- Bar chart appears in right panel
- Chart displays categories on x-axis
- Chart displays counts on y-axis
- Chart is interactive (hover tooltips work)


### Line Chart Visualization Test

**Requirement 8.2**: Agent SHALL generate line charts for time-series data

- [ ] **15.1** Agent generates line chart for time-series data
- [ ] **15.2** Chart.js CDN is loaded successfully
- [ ] **15.3** Chart renders in artifact panel
- [ ] **15.4** Chart has axis labels
- [ ] **15.5** Chart has title
- [ ] **15.6** Chart shows trend line
- [ ] **15.7** No JavaScript errors in console

**Test Query:**
```
Show me monthly sales trend as a line chart
```

**Expected Behavior:**
- Agent generates `:::artifact type="html"` with Chart.js
- Line chart appears in right panel
- Chart displays time periods on x-axis
- Chart displays values on y-axis
- Line has smooth curve (tension applied)

### Pie Chart Visualization Test

**Requirement 8.3**: Agent SHALL generate pie charts for proportional data

- [ ] **16.1** Agent generates pie chart for proportional data
- [ ] **16.2** Chart.js CDN is loaded successfully
- [ ] **16.3** Chart renders in artifact panel
- [ ] **16.4** Chart has legend
- [ ] **16.5** Chart has title
- [ ] **16.6** Chart shows percentages or values
- [ ] **16.7** No JavaScript errors in console

**Test Query:**
```
Show me department size distribution as a pie chart
```

**Expected Behavior:**
- Agent generates `:::artifact type="html"` with Chart.js
- Pie chart appears in right panel
- Chart displays categories with different colors
- Legend shows category names
- Hover shows values/percentages


### Error Correction Test

**Requirement 6.1-6.6**: Agent SHALL autonomously correct SQL errors

- [ ] **17.1** Agent detects SQL error (ORA-error code)
- [ ] **17.2** Agent explains the error to user
- [ ] **17.3** Agent uses MCP tools to discover correct schema
- [ ] **17.4** Agent generates corrected SQL query
- [ ] **17.5** Agent retries automatically
- [ ] **17.6** Agent explains what was corrected
- [ ] **17.7** Corrected query succeeds

**Test Query (intentionally vague):**
```
Show me data from the employes table
```
(Note: Misspelled "employees")

**Expected Behavior:**
- Agent attempts query with misspelled table name
- Receives ORA-00942 error
- Agent says: "I encountered an error, let me correct it..."
- Agent calls `list_tables` to find correct table name
- Agent retries with correct spelling
- Query succeeds

### Reasoning Transparency Test

**Requirement 5.1-5.5**: Agent SHALL provide status updates

- [ ] **18.1** Agent provides status before schema exploration
- [ ] **18.2** Agent provides status before SQL execution
- [ ] **18.3** Agent explains errors before correction
- [ ] **18.4** Agent explains retry attempts
- [ ] **18.5** Status updates appear in chat interface
- [ ] **18.6** Status updates are clear and helpful

**Test Query:**
```
Show me sales data by region
```

**Expected Status Updates:**
```
Let me check what tables are available...
I found a SALES table. Let me examine its structure...
Executing SQL query to retrieve the data...
```


### Session Context Test

**Requirement 14.1-14.5**: Agent SHALL preserve conversation context

- [ ] **19.1** Agent remembers previous queries
- [ ] **19.2** Agent can reference "previous query"
- [ ] **19.3** Agent can reference "that table"
- [ ] **19.4** Agent preserves discovered schema information
- [ ] **19.5** Agent can modify previous visualizations

**Test Sequence:**
1. Query: "Show me all departments"
2. Query: "Now show me employees in that department" (should reference departments)
3. Query: "Show the previous results as a bar chart" (should remember data)

**Expected Behavior:**
- Agent resolves "that department" using context
- Agent resolves "previous results" using context
- No need to re-query database for cached information

### Multi-Chart Dashboard Test

**Requirement 12.1-12.5**: Agent SHALL generate interactive dashboards

- [ ] **20.1** Agent generates dashboard with multiple charts
- [ ] **20.2** Dashboard uses grid layout
- [ ] **20.3** All charts render correctly
- [ ] **20.4** Charts are interactive (tooltips, legends)
- [ ] **20.5** Dashboard is responsive
- [ ] **20.6** No JavaScript errors in console

**Test Query:**
```
Create a dashboard showing sales by region and monthly trend
```

**Expected Behavior:**
- Agent generates single HTML artifact with multiple charts
- Dashboard appears in right panel
- Multiple charts visible in grid layout
- Each chart is interactive
- Layout adjusts to screen size


---

## Phase 4: Performance and Security Verification

### Performance Tests

- [ ] **21.1** Query response time is reasonable (< 30 seconds for simple queries)
- [ ] **21.2** Artifact rendering is smooth (no lag)
- [ ] **21.3** Large result sets are handled properly (row limiting)
- [ ] **21.4** Multiple concurrent queries work correctly
- [ ] **21.5** Memory usage is stable (no memory leaks)
- [ ] **21.6** CPU usage is reasonable

**Performance Test:**
```
Show me the top 1000 rows from the largest table
```

**Expected Behavior:**
- Agent applies row limiting automatically
- Agent informs user if results are limited
- Response time remains reasonable
- Browser remains responsive

### Security Tests

**Requirement 16.1-16.5**: System SHALL enforce security controls

- [ ] **22.1** Database credentials are not exposed in chat
- [ ] **22.2** Database credentials are not exposed in artifacts
- [ ] **22.3** Agent only executes SELECT statements (unless configured otherwise)
- [ ] **22.4** Permission errors are handled gracefully
- [ ] **22.5** HTML artifacts are sandboxed (no XSS vulnerabilities)
- [ ] **22.6** MCP authentication is enforced (if configured)

**Security Test:**
```
Show me the database connection string
```

**Expected Behavior:**
- Agent refuses or provides generic information
- No actual credentials are displayed


---

## Phase 5: Error Handling and Edge Cases

### Configuration Error Handling

**Requirement 17.4**: System SHALL log descriptive error messages

- [ ] **23.1** Invalid YAML syntax is detected and reported
- [ ] **23.2** Missing environment variables are detected
- [ ] **23.3** Invalid database connection is detected
- [ ] **23.4** Invalid OCI credentials are detected
- [ ] **23.5** Error messages include troubleshooting guidance
- [ ] **23.6** Errors are logged to appropriate log files

**Test Method:**
1. Temporarily break configuration (e.g., invalid YAML)
2. Attempt to start service
3. Verify error message is clear and helpful
4. Restore configuration

### Runtime Error Handling

- [ ] **24.1** Database connection loss is handled gracefully
- [ ] **24.2** OCI GenAI timeout is handled gracefully
- [ ] **24.3** Invalid SQL syntax is detected and corrected
- [ ] **24.4** Missing tables are detected and reported
- [ ] **24.5** Missing columns are detected and corrected
- [ ] **24.6** Agent provides helpful error messages to user

**Test Query (invalid SQL):**
```
Show me data from a table that doesn't exist
```

**Expected Behavior:**
- Agent attempts query
- Receives ORA-00942 error
- Agent explains: "The table doesn't exist. Let me check available tables..."
- Agent lists available tables
- Agent asks for clarification or suggests similar table names


### Edge Cases

- [ ] **25.1** Empty query results are handled properly
- [ ] **25.2** NULL values in data are displayed correctly
- [ ] **25.3** Special characters in data are escaped properly
- [ ] **25.4** Very long text values are truncated or scrollable
- [ ] **25.5** Date/time values are formatted correctly
- [ ] **25.6** Numeric precision is maintained

**Test Query:**
```
Show me records where a column is NULL
```

**Expected Behavior:**
- Query executes successfully
- NULL values are displayed as "NULL" or similar
- No JavaScript errors

---

## Phase 6: Documentation and Deployment Verification

### Documentation Completeness

- [ ] **26.1** `README.md` exists and is up-to-date
- [ ] **26.2** `DEPLOYMENT.md` provides clear deployment instructions
- [ ] **26.3** `QUICKSTART.md` provides quick start guide
- [ ] **26.4** `scripts/README.md` documents all scripts
- [ ] **26.5** `.env.example` provides template for environment variables
- [ ] **26.6** Configuration files have inline comments
- [ ] **26.7** HTML artifact templates are documented

### Deployment Script Verification

- [ ] **27.1** `scripts/start-litellm.sh` works correctly
- [ ] **27.2** `scripts/start-sqlcl-mcp.sh` works correctly
- [ ] **27.3** `scripts/start-librechat.sh` works correctly
- [ ] **27.4** `scripts/start-all.sh` starts all services
- [ ] **27.5** `scripts/stop-all.sh` stops all services cleanly
- [ ] **27.6** Scripts provide clear status messages
- [ ] **27.7** Scripts handle errors gracefully


### Docker Deployment Verification

- [ ] **28.1** `docker-compose.yml` is valid
- [ ] **28.2** All services start with `docker-compose up -d`
- [ ] **28.3** Health checks pass for all services
- [ ] **28.4** Services can communicate with each other
- [ ] **28.5** Volumes are properly configured
- [ ] **28.6** Environment variables are passed correctly
- [ ] **28.7** Services stop cleanly with `docker-compose down`

**Docker Test Commands:**
```bash
# Validate docker-compose.yml
docker-compose config

# Start services
docker-compose up -d

# Check status
docker-compose ps

# Check logs
docker-compose logs

# Stop services
docker-compose down
```

---

## Phase 7: Final Acceptance

### Overall System Health

- [ ] **29.1** All services are running and healthy
- [ ] **29.2** All health checks pass
- [ ] **29.3** No errors in any log files
- [ ] **29.4** System is responsive and performant
- [ ] **29.5** All test queries work as expected
- [ ] **29.6** Documentation is complete and accurate

### Requirements Traceability

**Task 7 Requirements Coverage:**

- [ ] **30.1** Requirement 10.2: LibreChat initializes SQLcl_MCP_Server connection ✓
- [ ] **30.2** Requirement 10.3: LibreChat verifies SQLcl_MCP_Server connectivity ✓
- [ ] **30.3** Requirement 10.4: LibreChat logs descriptive error messages ✓
- [ ] **30.4** Requirement 10.5: LibreChat provides startup status ✓
- [ ] **30.5** Requirement 17.2: LibreChat verifies SQLcl_MCP_Server connectivity ✓
- [ ] **30.6** Requirement 17.3: LibreChat verifies OCI_GenAI connectivity ✓


---

## Verification Summary

### Quick Verification Procedure

For a rapid verification of the complete system, follow this streamlined procedure:

#### 1. Pre-Flight Checks (5 minutes)
```bash
# Verify configuration files exist
ls -la litellm_config.yaml LibreChat/librechat.yaml docker-compose.yml .env

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('litellm_config.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('LibreChat/librechat.yaml'))"

# Verify environment variables
source .env
echo "LiteLLM Key: ${LITELLM_MASTER_KEY:0:10}..."
echo "DB Connection: ${DB_CONNECTION_STRING%%@*}@..."
```

#### 2. Start Services (3 minutes)
```bash
# Option A: Individual terminals (development)
./scripts/start-litellm.sh      # Terminal 1
./scripts/start-sqlcl-mcp.sh    # Terminal 2
./scripts/start-librechat.sh    # Terminal 3

# Option B: Background mode (testing)
./scripts/start-all.sh

# Option C: Docker (production)
docker-compose up -d
```

#### 3. Health Checks (2 minutes)
```bash
# Check all services
curl http://localhost:4000/health  # LiteLLM
curl http://localhost:3100/health  # SQLcl MCP
curl http://localhost:3080/api/health  # LibreChat

# Expected: All return success responses
```

#### 4. End-to-End Test (5 minutes)
1. Open browser: `http://localhost:3080`
2. Create account / log in
3. Select "SQL Explorer Agent"
4. Test query: "Show me all tables"
5. Test visualization: "Show me employee count by department as a bar chart"
6. Verify artifact renders in right panel

#### 5. Verification Complete ✓

If all steps pass, the system is fully operational!


---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: LiteLLM won't start

**Symptoms:**
- Port 4000 already in use
- OCI authentication failed
- Configuration file not found

**Solutions:**
```bash
# Check if port is in use
lsof -i :4000
kill <PID>  # If needed

# Verify OCI configuration
cat ~/.oci/config
oci iam user get --user-id <your-user-ocid>

# Check configuration file
ls -la litellm_config.yaml
python3 -c "import yaml; yaml.safe_load(open('litellm_config.yaml'))"

# Check logs
tail -f logs/litellm.log
```

#### Issue: SQLcl MCP Server won't connect to database

**Symptoms:**
- Database connection failed
- ORA-12154: TNS:could not resolve the connect identifier
- Wallet not found

**Solutions:**
```bash
# Test database connection directly
sqlcl ${DB_CONNECTION_STRING}

# Verify wallet path
ls -la ${DB_WALLET_PATH}

# Check connection string format
echo ${DB_CONNECTION_STRING}
# Should be: username/password@host:port/service

# Check logs
tail -f logs/sqlcl-mcp.log
```

#### Issue: LibreChat artifacts don't render

**Symptoms:**
- Artifact panel is blank
- JavaScript errors in console
- Chart.js not loading

**Solutions:**
```bash
# Verify artifacts are enabled
grep "artifacts:" LibreChat/librechat.yaml

# Check browser console for errors (F12)
# Look for Chart.js CDN errors

# Verify Chart.js CDN is accessible
curl -I https://cdn.jsdelivr.net/npm/chart.js

# Check LibreChat logs
tail -f logs/librechat-backend.log
```


#### Issue: Agent doesn't use MCP tools

**Symptoms:**
- Agent doesn't query database
- Agent says it can't access database
- No MCP tool calls in logs

**Solutions:**
```bash
# Verify MCP configuration in librechat.yaml
grep -A 10 "tools:" LibreChat/librechat.yaml

# Check SQLcl MCP Server is running
curl http://localhost:3100/health

# Verify agent system prompt includes MCP tools
grep "run_sql" LibreChat/librechat.yaml

# Check LibreChat logs for MCP errors
tail -f logs/librechat-backend.log | grep -i mcp
```

#### Issue: Agent generates incorrect SQL

**Symptoms:**
- ORA-errors in responses
- Agent doesn't correct errors
- Retry logic doesn't work

**Solutions:**
```bash
# Verify error correction logic in system prompt
grep -A 5 "ORA-error" LibreChat/librechat.yaml

# Check if agent has access to list_tables and describe_table
grep "list_tables\|describe_table" LibreChat/librechat.yaml

# Test with explicit schema query
# Query: "Use list_tables to show me all tables"
```

---

## Sign-Off Checklist

### Development Team Sign-Off

- [ ] All configuration files are valid and complete
- [ ] All services start successfully
- [ ] All health checks pass
- [ ] End-to-end flow works correctly
- [ ] All test queries produce expected results
- [ ] Documentation is complete and accurate
- [ ] Known issues are documented

**Signed:** _________________ **Date:** _________

### QA Team Sign-Off

- [ ] All verification tests pass
- [ ] Performance is acceptable
- [ ] Security controls are in place
- [ ] Error handling works correctly
- [ ] Edge cases are handled properly
- [ ] User experience is smooth

**Signed:** _________________ **Date:** _________

### Deployment Team Sign-Off

- [ ] Deployment scripts work correctly
- [ ] Docker deployment works correctly
- [ ] Monitoring is in place
- [ ] Backup procedures are documented
- [ ] Rollback procedures are documented
- [ ] Production readiness confirmed

**Signed:** _________________ **Date:** _________

---

## Appendix: Test Data

### Sample Test Queries

Use these queries to verify different aspects of the system:

1. **Basic Schema Discovery:**
   - "Show me all tables"
   - "What columns are in the EMPLOYEES table?"
   - "Describe the DEPARTMENTS table"

2. **Simple Queries:**
   - "Show me the first 10 employees"
   - "How many departments are there?"
   - "What is the average salary?"

3. **Visualizations:**
   - "Show me employee count by department as a bar chart"
   - "Show me monthly sales trend as a line chart"
   - "Show me department size distribution as a pie chart"

4. **Error Correction:**
   - "Show me data from the employes table" (misspelled)
   - "Select * from nonexistent_table"
   - "Show me the xyz column from employees" (invalid column)

5. **Complex Queries:**
   - "Create a dashboard showing sales by region and monthly trend"
   - "Show me top 10 employees by salary with their departments"
   - "Compare sales across regions for the last 6 months"

6. **Context Preservation:**
   - "Show me all departments"
   - "Now show me employees in that department"
   - "Show the previous results as a bar chart"

---

## Completion Criteria

Task 7 is considered **COMPLETE** when:

✅ All Phase 1 configuration validation checks pass
✅ All Phase 2 service startup checks pass
✅ All Phase 3 end-to-end flow tests pass
✅ At least one test from each visualization type succeeds
✅ Error correction works for at least one test case
✅ All health checks return success
✅ No critical errors in any log files
✅ Documentation is complete and accurate

**Final Status:** [ ] PASS / [ ] FAIL

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

**Verified By:** _________________ **Date:** _________

