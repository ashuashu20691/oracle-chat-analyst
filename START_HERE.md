# LibreChat OCI SQL Explorer - Quick Start

Your system is configured and ready to run locally!

## Configuration Summary

✅ **SQLcl MCP Server**: stdio mode (managed by LibreChat)
- Path: `/Users/ashukum/sqlcl/sqlcl/bin/sql`
- Mode: stdio (no separate server needed)

✅ **OCI GenAI**: Configured with your credentials
- Model: `google.gemini-2.5-flash`
- Endpoint: `https://inference.generativeai.us-chicago-1.oci.oraclecloud.com`
- Compartment: `ocid1.compartment.oc1..aaaaaaaa5jnmxes5yog6ucgnrfttaeckgqewgvfkhaybd32km2lv25fghc4a`

✅ **Deployment**: Local (not Docker)

## Start the System

### Option 1: Automated Script (Recommended)

```bash
./scripts/start-local.sh
```

This will:
1. Check prerequisites
2. Start LiteLLM proxy
3. Start LibreChat (which will manage SQLcl MCP automatically)
4. Show you the URLs and logs

### Option 2: Manual Start (for debugging)

**Terminal 1 - Start LiteLLM:**
```bash
source .env
litellm --config litellm_config.yaml --port 4000
```

**Terminal 2 - Start LibreChat:**
```bash
cd LibreChat
npm install  # First time only
npm run backend &
sleep 5
npm run frontend
```

## Access the Application

Open your browser to: **http://localhost:3080**

1. Create an account or log in
2. Select "SQL Explorer Agent" from the agent dropdown
3. Start querying your database!

## Test Queries

Try these to verify everything works:

```
Show me all tables
```

```
What columns are in the [TABLE_NAME] table?
```

```
Show me the first 10 rows from [TABLE_NAME]
```

```
Show me [data] as a bar chart
```

## View Logs

```bash
# LiteLLM logs
tail -f logs/litellm.log

# LibreChat logs
tail -f logs/librechat-backend.log
tail -f logs/librechat-frontend.log
```

## Stop Services

```bash
./scripts/stop-all.sh
```

## Troubleshooting

### LiteLLM won't start
- Check if port 4000 is in use: `lsof -i :4000`
- Verify OCI config: `cat ~/.oci/config`
- Check logs: `tail -f logs/litellm.log`

### LibreChat won't start
- Check if MongoDB is running: `pgrep mongod`
- Check if port 3080 is in use: `lsof -i :3080`
- Check logs: `tail -f logs/librechat-backend.log`

### SQLcl MCP not working
- Verify SQLcl path: `ls -la /Users/ashukum/sqlcl/sqlcl/bin/sql`
- Test SQLcl manually: `/Users/ashukum/sqlcl/sqlcl/bin/sql -mcp`
- Check LibreChat logs for MCP errors

### Agent doesn't respond
- Verify LiteLLM is running: `curl http://localhost:4000/health`
- Check LITELLM_MASTER_KEY matches in both services
- Check browser console for errors (F12)

## Next Steps

Once everything is running:
1. Test basic queries to verify database connectivity
2. Try different visualization types (bar, line, pie charts)
3. Test error correction by using wrong table names
4. Explore your database with natural language!

## Important Files

- `LibreChat/librechat.yaml` - Main configuration
- `litellm_config.yaml` - LiteLLM/OCI GenAI config
- `.env` - Environment variables
- `scripts/start-local.sh` - Startup script
- `scripts/stop-all.sh` - Shutdown script

Enjoy exploring your Oracle database with AI! 🚀
