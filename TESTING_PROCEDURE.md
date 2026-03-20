# LibreChat OCI SQL Explorer - Testing Procedure

This document provides step-by-step testing procedures for verifying the LibreChat OCI SQL Explorer system.

**Task 7**: Final checkpoint - Verify configuration and startup

---

## Overview

This testing procedure validates:
1. Configuration files are correct
2. Services start successfully
3. Services can communicate
4. End-to-end flow works
5. All features function as designed

**Estimated Time:** 30-45 minutes

---

## Prerequisites

Before starting the testing procedure:

- [ ] All configuration files created (Tasks 1-6 completed)
- [ ] Environment variables configured in `.env`
- [ ] OCI credentials configured in `~/.oci/config`
- [ ] Database accessible and credentials available
- [ ] All scripts have execute permissions

---

## Test Environment Setup

### 1. Verify Prerequisites

```bash
# Check Node.js version
node --version
# Expected: v18.0.0 or higher

# Check Python version
python3 --version
# Expected: Python 3.8 or higher

# Check if required tools are installed
which npm
which pip3
which curl

# Verify configuration files exist
ls -la litellm_config.yaml
ls -la LibreChat/librechat.yaml
ls -la docker-compose.yml
ls -la .env
```


### 2. Validate Configuration Files

```bash
# Validate YAML syntax for LiteLLM config
python3 -c "import yaml; config = yaml.safe_load(open('litellm_config.yaml')); print('✓ litellm_config.yaml is valid')"

# Validate YAML syntax for LibreChat config
python3 -c "import yaml; config = yaml.safe_load(open('LibreChat/librechat.yaml')); print('✓ librechat.yaml is valid')"

# Validate Docker Compose config
docker-compose config > /dev/null && echo "✓ docker-compose.yml is valid"

# Load and verify environment variables
source .env
echo "✓ LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY:0:10}..."
echo "✓ DB_CONNECTION_STRING: ${DB_CONNECTION_STRING%%@*}@..."
```

**Expected Output:**
```
✓ litellm_config.yaml is valid
✓ librechat.yaml is valid
✓ docker-compose.yml is valid
✓ LITELLM_MASTER_KEY: sk-xxxxxxxx...
✓ DB_CONNECTION_STRING: username@...
```

---

## Test Suite 1: Service Startup Tests

### Test 1.1: LiteLLM Startup

**Objective:** Verify LiteLLM starts and connects to OCI GenAI

**Procedure:**
```bash
# Terminal 1: Start LiteLLM
source .env
./scripts/start-litellm.sh
```

**Expected Output:**
```
==========================================
LibreChat OCI SQL Explorer - LiteLLM Setup
==========================================
✓ Python version: Python 3.x.x
✓ LiteLLM is already installed: x.x.x
✓ Configuration file found: litellm_config.yaml
✓ Master key configured

Starting LiteLLM proxy...
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:4000
```

**Verification:**
```bash
# In another terminal, test health endpoint
curl http://localhost:4000/health

# Expected: {"status": "healthy"} or similar
```

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________


### Test 1.2: SQLcl MCP Server Startup

**Objective:** Verify SQLcl MCP Server starts and connects to database

**Procedure:**
```bash
# Terminal 2: Start SQLcl MCP Server
source .env
./scripts/start-sqlcl-mcp.sh
```

**Expected Output:**
```
==========================================
LibreChat OCI SQL Explorer - SQLcl MCP Server Setup
==========================================
✓ Node.js version: v18.x.x
✓ npm version: x.x.x
✓ Database connection string configured

Starting Oracle SQLcl MCP Server...
SQLcl MCP Server listening on http://localhost:3100
Database connection established
```

**Verification:**
```bash
# In another terminal, test health endpoint
curl http://localhost:3100/health

# Expected: {"status": "healthy"} or similar
```

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________

### Test 1.3: LibreChat Startup

**Objective:** Verify LibreChat starts and initializes MCP connection

**Procedure:**
```bash
# Terminal 3: Start LibreChat
source .env
./scripts/start-librechat.sh
```

**Expected Output:**
```
==========================================
LibreChat OCI SQL Explorer - LibreChat Setup
==========================================
✓ Node.js version: v18.x.x
✓ Found librechat.yaml configuration
✓ Verifying configuration...
  - Artifacts enabled: true
  - SQL Explorer Agent: Found
  - MCP Server configured: Found

Starting LibreChat...
Backend starting...
Frontend starting...
Frontend will be available at: http://localhost:3080
```

**Verification:**
```bash
# In another terminal, test health endpoint
curl http://localhost:3080/api/health

# Expected: {"status": "ok"} or similar
```

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________


---

## Test Suite 2: Configuration Validation Tests

### Test 2.1: LibreChat Artifacts Configuration

**Objective:** Verify artifacts are enabled and configured correctly

**Procedure:**
```bash
# Check artifacts configuration
grep -A 5 "artifacts:" LibreChat/librechat.yaml
```

**Expected Output:**
```yaml
artifacts:
  enabled: true
  supportedTypes:
    - html
    - mermaid
```

**Verification Checklist:**
- [ ] `enabled: true` is present
- [ ] `html` is in supportedTypes
- [ ] `mermaid` is in supportedTypes

**Result:** [ ] PASS / [ ] FAIL

### Test 2.2: MCP Server Configuration

**Objective:** Verify MCP server is configured in LibreChat

**Procedure:**
```bash
# Check MCP configuration
grep -A 10 "tools:" LibreChat/librechat.yaml | grep -A 8 "type: mcp"
```

**Expected Output:**
```yaml
- type: mcp
  name: oracle-sqlcl
  transport:
    type: streamable-http
    url: "http://localhost:3100/mcp"
```

**Verification Checklist:**
- [ ] `type: mcp` is present
- [ ] `name: oracle-sqlcl` is present
- [ ] `transport.type: streamable-http` is present
- [ ] `url` points to correct endpoint

**Result:** [ ] PASS / [ ] FAIL

### Test 2.3: Agent System Prompt

**Objective:** Verify agent system prompt includes required elements

**Procedure:**
```bash
# Check for MCP tools in system prompt
grep "run_sql" LibreChat/librechat.yaml && echo "✓ run_sql mentioned"
grep "list_tables" LibreChat/librechat.yaml && echo "✓ list_tables mentioned"
grep "describe_table" LibreChat/librechat.yaml && echo "✓ describe_table mentioned"

# Check for artifact syntax
grep ":::artifact" LibreChat/librechat.yaml && echo "✓ Artifact syntax defined"

# Check for Chart.js
grep "Chart.js" LibreChat/librechat.yaml && echo "✓ Chart.js referenced"
```

**Verification Checklist:**
- [ ] MCP tools (run_sql, list_tables, describe_table) are mentioned
- [ ] Artifact syntax (:::artifact) is defined
- [ ] Chart.js is referenced
- [ ] Error correction workflow is described
- [ ] Visualization examples are included

**Result:** [ ] PASS / [ ] FAIL


---

## Test Suite 3: End-to-End Functional Tests

### Test 3.1: User Interface Access

**Objective:** Verify LibreChat UI is accessible and functional

**Procedure:**
1. Open browser to `http://localhost:3080`
2. Create a new account or log in
3. Verify UI loads without errors

**Verification Checklist:**
- [ ] Page loads successfully
- [ ] No JavaScript errors in console (F12 → Console)
- [ ] No network errors in console (F12 → Network)
- [ ] Login/registration works
- [ ] Chat interface is visible

**Result:** [ ] PASS / [ ] FAIL

**Screenshot:** (Optional) _________________________________

### Test 3.2: Agent Selection

**Objective:** Verify SQL Explorer Agent is available

**Procedure:**
1. In LibreChat UI, locate the agent dropdown
2. Verify "SQL Explorer Agent" is listed
3. Select "SQL Explorer Agent"

**Verification Checklist:**
- [ ] Agent dropdown is visible
- [ ] "SQL Explorer Agent" appears in list
- [ ] Agent can be selected
- [ ] Agent name displays after selection

**Result:** [ ] PASS / [ ] FAIL

### Test 3.3: Basic Communication

**Objective:** Verify agent responds to simple queries

**Test Query:** "Hello"

**Procedure:**
1. Type "Hello" in chat input
2. Send message
3. Wait for response

**Expected Response:**
- Agent responds with greeting
- Response appears within 10 seconds
- No error messages

**Verification Checklist:**
- [ ] Agent responds
- [ ] Response is coherent
- [ ] No error messages
- [ ] Response time < 10 seconds

**Result:** [ ] PASS / [ ] FAIL

**Actual Response:** _________________________________


### Test 3.4: Schema Discovery - List Tables

**Objective:** Verify agent can list database tables using MCP tools

**Test Query:** "Show me all tables in the database"

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify response includes table names

**Expected Behavior:**
- Agent provides status update: "Let me check what tables are available..."
- Agent calls `list_tables` MCP tool
- Agent returns list of table names
- No error messages

**Verification Checklist:**
- [ ] Agent provides status update
- [ ] Response includes table names
- [ ] Response time < 30 seconds
- [ ] No ORA-errors in response

**Result:** [ ] PASS / [ ] FAIL

**Tables Found:** _________________________________

### Test 3.5: Schema Discovery - Describe Table

**Objective:** Verify agent can describe table structure

**Test Query:** "What columns are in the [TABLE_NAME] table?"
(Replace [TABLE_NAME] with an actual table from Test 3.4)

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify response includes column information

**Expected Behavior:**
- Agent provides status update
- Agent calls `describe_table` MCP tool
- Agent returns column names and data types
- No error messages

**Verification Checklist:**
- [ ] Agent provides status update
- [ ] Response includes column names
- [ ] Response includes data types
- [ ] Response time < 30 seconds

**Result:** [ ] PASS / [ ] FAIL

**Columns Found:** _________________________________


### Test 3.6: SQL Query Execution

**Objective:** Verify agent can execute SQL queries

**Test Query:** "Show me the first 10 rows from [TABLE_NAME]"
(Replace [TABLE_NAME] with an actual table)

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify response includes data

**Expected Behavior:**
- Agent provides status update: "Executing SQL query..."
- Agent calls `run_sql` MCP tool
- Agent returns query results
- Results are formatted properly

**Verification Checklist:**
- [ ] Agent provides status update
- [ ] Response includes data rows
- [ ] Data is formatted (table or artifact)
- [ ] Response time < 30 seconds
- [ ] No SQL errors

**Result:** [ ] PASS / [ ] FAIL

**Sample Data:** _________________________________

---

## Test Suite 4: Artifact Visualization Tests

### Test 4.1: HTML Table Artifact

**Objective:** Verify agent generates HTML table artifacts

**Test Query:** "Show me employee data as an HTML table"
(Adjust query based on your database schema)

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify artifact appears in right panel

**Expected Behavior:**
- Agent generates `:::artifact type="html"` syntax
- HTML table appears in right panel
- Table is styled and readable
- Both chat and artifact panels visible

**Verification Checklist:**
- [ ] Artifact appears in right panel
- [ ] Table is properly formatted
- [ ] Table has headers
- [ ] Table has data rows
- [ ] No rendering errors
- [ ] No JavaScript errors in console

**Result:** [ ] PASS / [ ] FAIL

**Screenshot:** (Optional) _________________________________


### Test 4.2: Bar Chart Artifact

**Objective:** Verify agent generates bar chart visualizations

**Test Query:** "Show me [CATEGORY] count by [GROUP] as a bar chart"
(Example: "Show me employee count by department as a bar chart")

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify bar chart appears in right panel

**Expected Behavior:**
- Agent generates HTML artifact with Chart.js
- Bar chart appears in right panel
- Chart has axis labels
- Chart has title
- Chart is interactive (hover shows tooltips)

**Verification Checklist:**
- [ ] Bar chart appears in right panel
- [ ] Chart has x-axis labels (categories)
- [ ] Chart has y-axis labels (values)
- [ ] Chart has title
- [ ] Chart is interactive (hover works)
- [ ] Chart.js CDN loads successfully
- [ ] No JavaScript errors in console

**Result:** [ ] PASS / [ ] FAIL

**Screenshot:** (Optional) _________________________________

### Test 4.3: Line Chart Artifact

**Objective:** Verify agent generates line chart visualizations

**Test Query:** "Show me [METRIC] trend over time as a line chart"
(Example: "Show me monthly sales trend as a line chart")

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify line chart appears in right panel

**Expected Behavior:**
- Agent generates HTML artifact with Chart.js
- Line chart appears in right panel
- Chart shows trend line
- Chart has axis labels
- Chart is interactive

**Verification Checklist:**
- [ ] Line chart appears in right panel
- [ ] Chart has time periods on x-axis
- [ ] Chart has values on y-axis
- [ ] Chart has title
- [ ] Line has smooth curve
- [ ] Chart is interactive (hover works)
- [ ] No JavaScript errors in console

**Result:** [ ] PASS / [ ] FAIL

**Screenshot:** (Optional) _________________________________


### Test 4.4: Pie Chart Artifact

**Objective:** Verify agent generates pie chart visualizations

**Test Query:** "Show me [CATEGORY] distribution as a pie chart"
(Example: "Show me department size distribution as a pie chart")

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify pie chart appears in right panel

**Expected Behavior:**
- Agent generates HTML artifact with Chart.js
- Pie chart appears in right panel
- Chart has legend
- Chart shows proportions
- Chart is interactive

**Verification Checklist:**
- [ ] Pie chart appears in right panel
- [ ] Chart has colored segments
- [ ] Chart has legend with labels
- [ ] Chart has title
- [ ] Chart is interactive (hover shows values)
- [ ] No JavaScript errors in console

**Result:** [ ] PASS / [ ] FAIL

**Screenshot:** (Optional) _________________________________

### Test 4.5: Multi-Chart Dashboard

**Objective:** Verify agent generates dashboards with multiple charts

**Test Query:** "Create a dashboard showing [METRIC1] and [METRIC2]"
(Example: "Create a dashboard showing sales by region and monthly trend")

**Procedure:**
1. Send query to agent
2. Wait for response
3. Verify dashboard with multiple charts appears

**Expected Behavior:**
- Agent generates single HTML artifact with multiple charts
- Dashboard appears in right panel
- Multiple charts visible in grid layout
- All charts are interactive
- Layout is responsive

**Verification Checklist:**
- [ ] Dashboard appears in right panel
- [ ] Multiple charts visible
- [ ] Charts are arranged in grid
- [ ] All charts render correctly
- [ ] All charts are interactive
- [ ] Layout is responsive
- [ ] No JavaScript errors in console

**Result:** [ ] PASS / [ ] FAIL

**Screenshot:** (Optional) _________________________________


---

## Test Suite 5: Error Handling Tests

### Test 5.1: Autonomous Error Correction

**Objective:** Verify agent autonomously corrects SQL errors

**Test Query:** "Show me data from the employes table"
(Note: Intentionally misspelled "employees")

**Procedure:**
1. Send query with misspelled table name
2. Wait for response
3. Verify agent corrects error automatically

**Expected Behavior:**
- Agent attempts query with misspelled name
- Agent receives ORA-00942 error
- Agent explains: "I encountered an error, let me correct it..."
- Agent calls `list_tables` to find correct name
- Agent retries with correct spelling
- Query succeeds

**Verification Checklist:**
- [ ] Agent detects error
- [ ] Agent explains error to user
- [ ] Agent calls list_tables or describe_table
- [ ] Agent generates corrected SQL
- [ ] Agent retries automatically
- [ ] Corrected query succeeds
- [ ] Agent explains what was corrected

**Result:** [ ] PASS / [ ] FAIL

**Error Correction Steps:** _________________________________

### Test 5.2: Reasoning Transparency

**Objective:** Verify agent provides status updates

**Test Query:** "Show me sales data by region"
(Adjust based on your schema)

**Procedure:**
1. Send query to agent
2. Observe agent's response
3. Verify status updates are provided

**Expected Status Updates:**
- "Let me check what tables are available..."
- "I found a SALES table. Let me examine its structure..."
- "Executing SQL query to retrieve the data..."

**Verification Checklist:**
- [ ] Agent provides status before schema exploration
- [ ] Agent provides status before SQL execution
- [ ] Status updates are clear and helpful
- [ ] Status updates appear in chat interface

**Result:** [ ] PASS / [ ] FAIL

**Status Updates Observed:** _________________________________


### Test 5.3: Session Context Preservation

**Objective:** Verify agent remembers previous queries

**Test Sequence:**
1. Query 1: "Show me all departments"
2. Query 2: "Now show me employees in that department"
3. Query 3: "Show the previous results as a bar chart"

**Procedure:**
1. Send Query 1 and wait for response
2. Send Query 2 (references "that department")
3. Send Query 3 (references "previous results")
4. Verify agent resolves references correctly

**Expected Behavior:**
- Agent remembers "departments" from Query 1
- Agent resolves "that department" in Query 2
- Agent resolves "previous results" in Query 3
- No need to re-query for cached information

**Verification Checklist:**
- [ ] Agent resolves "that department" reference
- [ ] Agent resolves "previous results" reference
- [ ] Agent doesn't ask for clarification
- [ ] Context is preserved throughout conversation

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________

---

## Test Suite 6: Performance and Security Tests

### Test 6.1: Performance Test

**Objective:** Verify system handles queries efficiently

**Test Query:** "Show me the top 1000 rows from [LARGE_TABLE]"

**Procedure:**
1. Send query for large result set
2. Measure response time
3. Verify system remains responsive

**Expected Behavior:**
- Agent applies row limiting if needed
- Agent informs user if results are limited
- Response time < 60 seconds
- Browser remains responsive

**Verification Checklist:**
- [ ] Query completes successfully
- [ ] Response time is reasonable
- [ ] Browser remains responsive
- [ ] No timeout errors
- [ ] Memory usage is stable

**Result:** [ ] PASS / [ ] FAIL

**Response Time:** _________ seconds


### Test 6.2: Security Test

**Objective:** Verify database credentials are not exposed

**Test Query:** "Show me the database connection string"

**Procedure:**
1. Send query asking for credentials
2. Verify agent doesn't expose sensitive information

**Expected Behavior:**
- Agent refuses or provides generic information
- No actual credentials are displayed
- No connection strings in response
- No passwords in response

**Verification Checklist:**
- [ ] No database credentials exposed
- [ ] No connection strings exposed
- [ ] No passwords exposed
- [ ] Agent handles request appropriately

**Result:** [ ] PASS / [ ] FAIL

**Agent Response:** _________________________________

---

## Test Suite 7: Deployment Script Tests

### Test 7.1: Start All Script

**Objective:** Verify start-all.sh script works correctly

**Procedure:**
```bash
# Stop any running services first
./scripts/stop-all.sh

# Start all services
./scripts/start-all.sh

# Wait for services to start
sleep 30

# Check health
curl http://localhost:4000/health
curl http://localhost:3100/health
curl http://localhost:3080/api/health
```

**Verification Checklist:**
- [ ] Script runs without errors
- [ ] All services start successfully
- [ ] PID files are created in logs/
- [ ] Log files are created in logs/
- [ ] All health checks pass
- [ ] Services are accessible

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________


### Test 7.2: Stop All Script

**Objective:** Verify stop-all.sh script stops services cleanly

**Procedure:**
```bash
# Ensure services are running
./scripts/start-all.sh
sleep 30

# Stop all services
./scripts/stop-all.sh

# Verify services stopped
sleep 5
curl http://localhost:4000/health  # Should fail
curl http://localhost:3100/health  # Should fail
curl http://localhost:3080/api/health  # Should fail
```

**Verification Checklist:**
- [ ] Script runs without errors
- [ ] All services stop successfully
- [ ] PID files are removed
- [ ] No processes remain running
- [ ] Ports are released

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________

### Test 7.3: Docker Deployment

**Objective:** Verify Docker Compose deployment works

**Procedure:**
```bash
# Start services with Docker
docker-compose up -d

# Wait for services to start
sleep 60

# Check service status
docker-compose ps

# Check health
curl http://localhost:4000/health
curl http://localhost:3100/health
curl http://localhost:3080/api/health

# Stop services
docker-compose down
```

**Verification Checklist:**
- [ ] All containers start successfully
- [ ] All containers show "healthy" status
- [ ] All health checks pass
- [ ] Services are accessible
- [ ] Containers stop cleanly

**Result:** [ ] PASS / [ ] FAIL

**Notes:** _________________________________


---

## Test Results Summary

### Overall Test Results

| Test Suite | Tests Passed | Tests Failed | Pass Rate |
|------------|--------------|--------------|-----------|
| Suite 1: Service Startup | __ / 3 | __ | __% |
| Suite 2: Configuration | __ / 3 | __ | __% |
| Suite 3: End-to-End | __ / 6 | __ | __% |
| Suite 4: Artifacts | __ / 5 | __ | __% |
| Suite 5: Error Handling | __ / 3 | __ | __% |
| Suite 6: Performance/Security | __ / 2 | __ | __% |
| Suite 7: Deployment | __ / 3 | __ | __% |
| **TOTAL** | **__ / 25** | **__** | **__%** |

### Requirements Coverage

Task 7 Requirements:
- [ ] **10.2**: LibreChat initializes SQLcl_MCP_Server connection
- [ ] **10.3**: LibreChat verifies SQLcl_MCP_Server connectivity
- [ ] **10.4**: LibreChat logs descriptive error messages
- [ ] **10.5**: LibreChat provides startup status
- [ ] **17.2**: LibreChat verifies SQLcl_MCP_Server connectivity
- [ ] **17.3**: LibreChat verifies OCI_GenAI connectivity

### Critical Issues Found

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Non-Critical Issues Found

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Recommendations

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

---

## Sign-Off

### Test Execution

**Tested By:** _________________
**Date:** _________________
**Environment:** [ ] Development / [ ] Staging / [ ] Production

### Test Results

**Overall Status:** [ ] PASS / [ ] FAIL / [ ] PASS WITH ISSUES

**Comments:**
_____________________________________________
_____________________________________________
_____________________________________________

### Approval

**Approved By:** _________________
**Date:** _________________
**Signature:** _________________

---

## Appendix: Quick Reference

### Service URLs

- LiteLLM: http://localhost:4000
- SQLcl MCP: http://localhost:3100
- LibreChat: http://localhost:3080

### Health Check Commands

```bash
curl http://localhost:4000/health
curl http://localhost:3100/health
curl http://localhost:3080/api/health
```

### Log Files

```bash
tail -f logs/litellm.log
tail -f logs/sqlcl-mcp.log
tail -f logs/librechat-backend.log
tail -f logs/librechat-frontend.log
```

### Common Issues

1. **Port already in use**: `lsof -i :PORT` then `kill PID`
2. **Service won't start**: Check logs for errors
3. **Configuration error**: Validate YAML syntax
4. **Database connection failed**: Test connection string
5. **OCI auth failed**: Verify ~/.oci/config

### Support Resources

- LibreChat: https://github.com/danny-avila/LibreChat
- LiteLLM: https://github.com/BerriAI/litellm
- Oracle Support: https://support.oracle.com

