# Deployment Scripts

This directory contains scripts for installing and managing the LibreChat OCI SQL Explorer services.

## Available Scripts

### Individual Service Scripts

#### `start-litellm.sh`
Installs and starts the LiteLLM proxy for OCI GenAI.

**Prerequisites:**
- Python 3.8+
- pip3
- `litellm_config.yaml` in project root
- `LITELLM_MASTER_KEY` environment variable

**Usage:**
```bash
export LITELLM_MASTER_KEY="sk-your-key"
./scripts/start-litellm.sh
```

**What it does:**
1. Checks Python and pip installation
2. Installs LiteLLM if not present
3. Validates configuration file
4. Generates master key if not set
5. Starts LiteLLM on port 4000 (default)

---

#### `start-sqlcl-mcp.sh`
Installs and starts the Oracle SQLcl MCP Server.

**Prerequisites:**
- Node.js 18+
- npm
- `DB_CONNECTION_STRING` environment variable
- `DB_WALLET_PATH` (optional, for Autonomous DB)

**Usage:**
```bash
export DB_CONNECTION_STRING="user/pass@host:port/service"
export DB_WALLET_PATH="/path/to/wallet"  # Optional
./scripts/start-sqlcl-mcp.sh
```

**What it does:**
1. Checks Node.js and npm installation
2. Installs SQLcl MCP Server if not present
3. Validates database connection string
4. Starts SQLcl MCP Server on port 3100 (default)

---

#### `start-librechat.sh`
Configures and starts LibreChat.

**Prerequisites:**
- Node.js 18+
- npm
- `LibreChat/librechat.yaml` configuration file
- `LITELLM_MASTER_KEY` environment variable
- LiteLLM and SQLcl MCP Server running

**Usage:**
```bash
export LITELLM_MASTER_KEY="sk-your-key"
./scripts/start-librechat.sh
```

**What it does:**
1. Checks Node.js and npm installation
2. Validates configuration files
3. Installs dependencies if needed
4. Verifies LiteLLM and SQLcl MCP connectivity
5. Starts LibreChat backend and frontend

---

### Convenience Scripts

#### `start-all.sh`
Starts all services in the background with a single command.

**Prerequisites:**
- All prerequisites from individual scripts
- `.env` file with all required variables

**Usage:**
```bash
./scripts/start-all.sh
```

**What it does:**
1. Loads environment variables from `.env`
2. Creates logs directory
3. Checks if ports are available
4. Starts LiteLLM in background
5. Starts SQLcl MCP Server in background
6. Starts LibreChat backend and frontend
7. Waits for each service to be ready
8. Displays service status and log locations

**Output:**
- Logs: `logs/litellm.log`, `logs/sqlcl-mcp.log`, `logs/librechat-backend.log`, `logs/librechat-frontend.log`
- PID files: `logs/*.pid`

---

#### `stop-all.sh`
Stops all running services.

**Usage:**
```bash
./scripts/stop-all.sh
```

**What it does:**
1. Reads PID files from logs directory
2. Stops each service gracefully
3. Force kills if necessary
4. Cleans up PID files
5. Performs additional cleanup for stray processes

---

## Environment Variables

All scripts use these environment variables (typically set in `.env`):

### Required
- `LITELLM_MASTER_KEY` - Authentication key for LiteLLM
- `DB_CONNECTION_STRING` - Database connection string

### Optional
- `DB_WALLET_PATH` - Path to Oracle wallet (for Autonomous DB)
- `LITELLM_PORT` - LiteLLM port (default: 4000)
- `SQLCL_MCP_PORT` - SQLcl MCP port (default: 3100)

## Usage Patterns

### Development (Individual Scripts)

Use individual scripts when you want to:
- See real-time logs in terminal
- Debug specific services
- Restart individual services

**Terminal 1:**
```bash
source .env
./scripts/start-litellm.sh
```

**Terminal 2:**
```bash
source .env
./scripts/start-sqlcl-mcp.sh
```

**Terminal 3:**
```bash
source .env
./scripts/start-librechat.sh
```

### Development (All Services)

Use `start-all.sh` when you want to:
- Start everything quickly
- Run services in background
- View logs in files

```bash
./scripts/start-all.sh

# View logs
tail -f logs/litellm.log
tail -f logs/sqlcl-mcp.log
tail -f logs/librechat-backend.log

# Stop when done
./scripts/stop-all.sh
```

### Production

For production, use Docker Compose instead:
```bash
docker-compose up -d
```

## Troubleshooting

### Script Won't Execute

**Problem:** `Permission denied`

**Solution:**
```bash
chmod +x scripts/*.sh
```

---

### Port Already in Use

**Problem:** `Port 4000 is already in use`

**Solution:**
```bash
# Find process using the port
lsof -i :4000

# Kill the process
kill <PID>

# Or use a different port
export LITELLM_PORT=4001
```

---

### Service Won't Start

**Problem:** Service fails to start

**Solution:**
1. Check logs in `logs/` directory
2. Verify environment variables are set
3. Check prerequisites are installed
4. Verify configuration files exist

---

### Service Not Responding

**Problem:** Service started but not responding

**Solution:**
```bash
# Check if service is running
ps aux | grep litellm
ps aux | grep sqlcl-mcp-server

# Check service health
curl http://localhost:4000/health
curl http://localhost:3100/health
curl http://localhost:3080/api/health

# Check logs for errors
tail -f logs/litellm.log
tail -f logs/sqlcl-mcp.log
```

---

### Can't Stop Services

**Problem:** `stop-all.sh` doesn't stop services

**Solution:**
```bash
# Manually kill processes
pkill -f litellm
pkill -f sqlcl-mcp-server
pkill -f "npm run backend"
pkill -f "npm run frontend"

# Remove stale PID files
rm -f logs/*.pid
```

## Log Files

All scripts write logs to the `logs/` directory:

- `logs/litellm.log` - LiteLLM proxy logs
- `logs/sqlcl-mcp.log` - SQLcl MCP Server logs
- `logs/librechat-backend.log` - LibreChat backend logs
- `logs/librechat-frontend.log` - LibreChat frontend logs

PID files for background processes:
- `logs/litellm.pid`
- `logs/sqlcl-mcp.pid`
- `logs/librechat-backend.pid`
- `logs/librechat-frontend.pid`

## Health Checks

Check if services are running:

```bash
# LiteLLM
curl http://localhost:4000/health

# SQLcl MCP Server
curl http://localhost:3100/health

# LibreChat
curl http://localhost:3080/api/health
```

## Script Maintenance

### Adding a New Service

1. Create `start-<service>.sh` script
2. Follow the pattern of existing scripts:
   - Check prerequisites
   - Validate configuration
   - Start service
   - Provide status feedback
3. Update `start-all.sh` to include new service
4. Update `stop-all.sh` to stop new service
5. Update this README

### Modifying Scripts

When modifying scripts:
1. Test changes thoroughly
2. Update error messages
3. Update this README
4. Maintain consistent style
5. Add comments for complex logic

## Best Practices

1. **Always use `.env` file** - Don't hardcode credentials
2. **Check logs first** - Most issues are visible in logs
3. **Use health checks** - Verify services are responding
4. **Stop cleanly** - Use `stop-all.sh` instead of killing processes
5. **Monitor resources** - Check CPU/memory usage for long-running services

## Security Notes

1. **Protect `.env` file** - Never commit to version control
2. **Secure log files** - May contain sensitive information
3. **Use strong keys** - Generate random keys for secrets
4. **Limit permissions** - `chmod 600 .env` and wallet files
5. **Monitor access** - Review logs for unauthorized access

## Performance Tips

1. **Use background mode** - `start-all.sh` for better performance
2. **Monitor logs** - Watch for errors and warnings
3. **Check resources** - Ensure adequate CPU/memory
4. **Optimize database** - Use indexes and connection pooling
5. **Cache responses** - Enable caching in LiteLLM

## Support

For issues with:
- **Scripts**: Check logs and this README
- **LiteLLM**: https://github.com/BerriAI/litellm
- **SQLcl MCP**: Oracle Support
- **LibreChat**: https://github.com/danny-avila/LibreChat
