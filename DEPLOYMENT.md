# LibreChat OCI SQL Explorer - Deployment Guide

This guide provides instructions for deploying the LibreChat OCI SQL Explorer system using either standalone scripts or Docker Compose.

## Prerequisites

### Required Software

- **Node.js 18+** - For LibreChat and SQLcl MCP Server
- **Python 3.8+** - For LiteLLM
- **Docker & Docker Compose** (optional) - For containerized deployment
- **Oracle Database 23ai** - Accessible database instance
- **OCI GenAI Access** - Oracle Cloud Infrastructure Generative AI service

### Required Credentials

1. **OCI Configuration** (`~/.oci/config`):
   - OCI API key
   - Tenancy OCID
   - User OCID
   - Fingerprint
   - Region

2. **Database Connection**:
   - Database username and password
   - Database host, port, and service name
   - Wallet files (if using Autonomous Database)

## Deployment Options

### Option 1: Standalone Scripts (Development)

This option runs each service in a separate terminal window. Best for development and testing.

#### Step 1: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the template
cp .env.example .env

# Edit the file with your credentials
nano .env
```

Required variables:
```bash
# LiteLLM Master Key (generate with: openssl rand -hex 16)
export LITELLM_MASTER_KEY="sk-your-master-key-here"

# Database Connection
export DB_CONNECTION_STRING="username/password@host:port/service"
export DB_WALLET_PATH="/path/to/wallet"  # Optional, for Autonomous DB

# Optional: Custom ports
export LITELLM_PORT=4000
export SQLCL_MCP_PORT=3100
```

#### Step 2: Start LiteLLM (Terminal 1)

```bash
# Make script executable
chmod +x scripts/start-litellm.sh

# Load environment variables
source .env

# Start LiteLLM
./scripts/start-litellm.sh
```

Expected output:
```
==========================================
LibreChat OCI SQL Explorer - LiteLLM Setup
==========================================
Python version: Python 3.x.x
LiteLLM is already installed: x.x.x
Starting LiteLLM proxy...
Configuration file: litellm_config.yaml
Port: 4000
Master Key: sk-xxxxxxxx...

INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:4000
```

#### Step 3: Start SQLcl MCP Server (Terminal 2)

```bash
# Make script executable
chmod +x scripts/start-sqlcl-mcp.sh

# Load environment variables
source .env

# Start SQLcl MCP Server
./scripts/start-sqlcl-mcp.sh
```

Expected output:
```
==========================================
LibreChat OCI SQL Explorer - SQLcl MCP Server Setup
==========================================
Node.js version: v18.x.x
npm version: x.x.x
Starting Oracle SQLcl MCP Server...
Port: 3100
Transport: streamable-http
Database: username@...

SQLcl MCP Server listening on http://localhost:3100
```

#### Step 4: Start LibreChat (Terminal 3)

```bash
# Make script executable
chmod +x scripts/start-librechat.sh

# Load environment variables
source .env

# Start LibreChat
./scripts/start-librechat.sh
```

Expected output:
```
==========================================
LibreChat OCI SQL Explorer - LibreChat Setup
==========================================
Node.js version: v18.x.x
Found librechat.yaml configuration
Verifying configuration...
  - Artifacts enabled: enabled: true
  - SQL Explorer Agent: Found
  - MCP Server configured: Found

Starting LibreChat...
Frontend will be available at: http://localhost:3080
```

#### Step 5: Access LibreChat

Open your browser to: **http://localhost:3080**

1. Create an account or log in
2. Select "SQL Explorer Agent" from the agent dropdown
3. Start exploring your database with natural language queries!

### Option 2: Docker Compose (Production)

This option runs all services in containers. Best for production deployments.

#### Step 1: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the template
cp .env.example .env

# Edit the file with your credentials
nano .env
```

Required variables:
```bash
# LiteLLM Master Key
LITELLM_MASTER_KEY=sk-your-master-key-here

# Database Connection
DB_CONNECTION_STRING=username/password@host:port/service
DB_WALLET_PATH=./wallet  # Path to wallet directory
```

#### Step 2: Prepare Wallet (if using Autonomous Database)

```bash
# Create wallet directory
mkdir -p wallet

# Copy wallet files to the directory
cp /path/to/downloaded/wallet/* wallet/

# Ensure proper permissions
chmod 600 wallet/*
```

#### Step 3: Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

Expected output:
```
NAME                      STATUS              PORTS
librechat-app             Up (healthy)        0.0.0.0:3080->3080/tcp
librechat-litellm         Up (healthy)        0.0.0.0:4000->4000/tcp
librechat-mongodb         Up (healthy)        27017/tcp
librechat-sqlcl-mcp       Up (healthy)        0.0.0.0:3100->3100/tcp
```

#### Step 4: Access LibreChat

Open your browser to: **http://localhost:3080**

#### Step 5: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Verification

### Test LiteLLM Connection

```bash
curl http://localhost:4000/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test SQLcl MCP Server Connection

```bash
curl http://localhost:3100/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test LibreChat

1. Open http://localhost:3080
2. Log in or create an account
3. Select "SQL Explorer Agent"
4. Send a test query: "Show me all tables"
5. Verify the agent responds with a list of tables

## Troubleshooting

### LiteLLM Issues

**Problem**: `OCI authentication failed`

**Solution**:
1. Verify `~/.oci/config` exists and is properly configured
2. Check OCI credentials: `oci iam user get --user-id <user-ocid>`
3. Verify compartment ID is correct
4. Ensure OCI GenAI service is enabled in your region

**Problem**: `Connection refused on port 4000`

**Solution**:
1. Check if LiteLLM is running: `ps aux | grep litellm`
2. Check logs for errors
3. Verify port 4000 is not in use: `lsof -i :4000`

### SQLcl MCP Server Issues

**Problem**: `Database connection failed`

**Solution**:
1. Test database connection: `sqlcl username/password@host:port/service`
2. Verify connection string format
3. Check firewall rules allow database port
4. If using wallet, verify `DB_WALLET_PATH` is correct

**Problem**: `Connection refused on port 3100`

**Solution**:
1. Check if SQLcl MCP Server is running: `ps aux | grep sqlcl`
2. Check logs for errors
3. Verify port 3100 is not in use: `lsof -i :3100`

### LibreChat Issues

**Problem**: `Artifacts don't render`

**Solution**:
1. Verify `artifacts.enabled: true` in `librechat.yaml`
2. Check browser console for JavaScript errors
3. Verify Chart.js CDN is accessible: `curl https://cdn.jsdelivr.net/npm/chart.js`
4. Clear browser cache and reload

**Problem**: `MCP tools not available`

**Solution**:
1. Verify SQLcl MCP Server is running and accessible
2. Check `librechat.yaml` has correct MCP configuration
3. Verify `mcpSettings.allowedDomains` includes 'localhost'
4. Check LibreChat logs for MCP initialization errors

**Problem**: `Agent doesn't respond`

**Solution**:
1. Verify LiteLLM is running and accessible
2. Check `LITELLM_MASTER_KEY` matches in both services
3. Verify OCI GenAI endpoint is accessible
4. Check LibreChat logs for API errors

### Docker Compose Issues

**Problem**: `Service unhealthy`

**Solution**:
1. Check service logs: `docker-compose logs <service-name>`
2. Verify environment variables are set correctly
3. Check network connectivity between containers
4. Restart unhealthy service: `docker-compose restart <service-name>`

**Problem**: `Cannot connect to MongoDB`

**Solution**:
1. Verify MongoDB is running: `docker-compose ps mongodb`
2. Check MongoDB logs: `docker-compose logs mongodb`
3. Verify `MONGO_URI` in LibreChat environment
4. Ensure MongoDB volume has proper permissions

## Configuration Files

### librechat.yaml

Located at: `LibreChat/librechat.yaml`

Key sections:
- `artifacts`: Enable split-screen visualization
- `endpoints.custom`: LiteLLM proxy configuration
- `agents`: SQL Explorer Agent with system prompt
- `agents.tools`: MCP server configuration

### litellm_config.yaml

Located at: `litellm_config.yaml`

Key sections:
- `model_list`: OCI GenAI model configuration
- `litellm_params`: API endpoint and authentication
- `general_settings`: Master key configuration

## Security Considerations

1. **Credentials**: Never commit `.env` file or credentials to version control
2. **Master Key**: Use a strong random key for `LITELLM_MASTER_KEY`
3. **Database Access**: Use read-only database user for exploration
4. **Wallet Security**: Protect wallet files with proper permissions (600)
5. **Network**: Use firewall rules to restrict access to services
6. **HTTPS**: Use reverse proxy (nginx, traefik) for HTTPS in production

## Performance Tuning

### LiteLLM

- Adjust `max_parallel_requests` in `litellm_config.yaml`
- Enable caching for repeated queries
- Monitor OCI GenAI quotas and limits

### SQLcl MCP Server

- Use connection pooling for multiple concurrent users
- Optimize database queries with proper indexes
- Monitor database performance metrics

### LibreChat

- Configure MongoDB with proper indexes
- Adjust Node.js memory limits if needed
- Use CDN for static assets in production

## Monitoring

### Health Checks

```bash
# Check all services
curl http://localhost:4000/health  # LiteLLM
curl http://localhost:3100/health  # SQLcl MCP
curl http://localhost:3080/api/health  # LibreChat
```

### Logs

```bash
# Standalone deployment
tail -f logs/litellm.log
tail -f logs/sqlcl-mcp.log
tail -f logs/librechat.log

# Docker deployment
docker-compose logs -f litellm
docker-compose logs -f sqlcl-mcp
docker-compose logs -f librechat
```

## Backup and Recovery

### MongoDB Backup

```bash
# Backup MongoDB data
docker-compose exec mongodb mongodump --out /backup

# Restore MongoDB data
docker-compose exec mongodb mongorestore /backup
```

### Configuration Backup

```bash
# Backup configuration files
tar -czf config-backup.tar.gz \
  librechat.yaml \
  litellm_config.yaml \
  .env \
  wallet/
```

## Upgrading

### Standalone Deployment

```bash
# Update LiteLLM
pip3 install --upgrade litellm

# Update SQLcl MCP Server
npm update -g @oracle/sqlcl-mcp-server

# Update LibreChat
cd LibreChat
git pull
npm install
```

### Docker Deployment

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d
```

## Support

For issues and questions:
- LibreChat: https://github.com/danny-avila/LibreChat
- LiteLLM: https://github.com/BerriAI/litellm
- Oracle SQLcl MCP Server: Oracle Support
- OCI GenAI: Oracle Cloud Support
