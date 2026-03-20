# LibreChat OCI SQL Explorer - Quick Start Guide

Get up and running in 5 minutes with this quick start guide.

## Prerequisites Checklist

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Oracle Database 23ai accessible
- [ ] OCI GenAI service access configured (`~/.oci/config`)
- [ ] Database credentials ready

## Quick Start (Standalone)

### 1. Configure Environment (2 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Minimum required configuration:
```bash
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 16)
DB_CONNECTION_STRING=username/password@host:port/service
```

### 2. Start Services (3 minutes)

Open three terminal windows:

**Terminal 1 - LiteLLM:**
```bash
source .env
./scripts/start-litellm.sh
```

**Terminal 2 - SQLcl MCP Server:**
```bash
source .env
./scripts/start-sqlcl-mcp.sh
```

**Terminal 3 - LibreChat:**
```bash
source .env
./scripts/start-librechat.sh
```

### 3. Access LibreChat

Open browser: **http://localhost:3080**

1. Create account
2. Select "SQL Explorer Agent"
3. Try: "Show me all tables"

## Quick Start (Docker)

### 1. Configure Environment

```bash
cp .env.example .env
nano .env
```

### 2. Start All Services

```bash
docker-compose up -d
```

### 3. Access LibreChat

Open browser: **http://localhost:3080**

## Example Queries

Try these queries with the SQL Explorer Agent:

1. **List Tables:**
   ```
   Show me all tables in the database
   ```

2. **Explore Data:**
   ```
   Show me the top 10 rows from the employees table
   ```

3. **Visualize Data:**
   ```
   Show me sales by region as a bar chart
   ```

4. **Time Series:**
   ```
   Show me monthly revenue trend as a line chart
   ```

5. **Dashboard:**
   ```
   Create a dashboard showing sales by region and monthly trend
   ```

## Troubleshooting

### Services Not Starting?

```bash
# Check if ports are in use
lsof -i :4000  # LiteLLM
lsof -i :3100  # SQLcl MCP
lsof -i :3080  # LibreChat

# Check service health
curl http://localhost:4000/health
curl http://localhost:3100/health
curl http://localhost:3080/api/health
```

### Database Connection Failed?

```bash
# Test database connection
sqlcl username/password@host:port/service

# Verify connection string format
echo $DB_CONNECTION_STRING
```

### OCI Authentication Failed?

```bash
# Verify OCI configuration
cat ~/.oci/config

# Test OCI CLI
oci iam user get --user-id <your-user-ocid>
```

## Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide
- Review [LibreChat/librechat.yaml](LibreChat/librechat.yaml) for configuration options
- Check [litellm_config.yaml](litellm_config.yaml) for OCI GenAI settings
- Explore HTML artifact templates in `.kiro/specs/librechat-oci-sql-explorer/templates/`

## Getting Help

- **LibreChat Issues**: https://github.com/danny-avila/LibreChat/issues
- **LiteLLM Issues**: https://github.com/BerriAI/litellm/issues
- **Oracle Support**: https://support.oracle.com

## Architecture Overview

```
┌─────────────┐
│   Browser   │
│ (Port 3080) │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  LibreChat  │────▶│   LiteLLM    │────▶│ OCI GenAI   │
│             │     │  (Port 4000) │     │             │
└──────┬──────┘     └──────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│ SQLcl MCP   │────▶│   Oracle     │
│ (Port 3100) │     │  Database    │
└─────────────┘     └──────────────┘
```

## Key Features

✅ **Natural Language Queries** - Ask questions in plain English
✅ **Automatic Visualizations** - Charts and tables generated automatically
✅ **Error Correction** - Agent fixes SQL errors autonomously
✅ **Schema Discovery** - No need to know database structure
✅ **Split-Screen UI** - Chat and visualizations side-by-side
✅ **Interactive Charts** - Powered by Chart.js
✅ **Session Context** - Agent remembers previous queries

## Security Notes

- Never commit `.env` file to version control
- Use read-only database user for exploration
- Protect wallet files with proper permissions (chmod 600)
- Use strong random keys for all secrets
- Consider HTTPS reverse proxy for production

## Performance Tips

- Use database indexes for frequently queried columns
- Limit large result sets with FETCH FIRST clause
- Monitor OCI GenAI quotas and rate limits
- Use connection pooling for multiple users
- Cache frequently accessed schema information

Enjoy exploring your Oracle database with AI! 🚀
