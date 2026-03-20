#!/bin/bash
# LibreChat OCI SQL Explorer - SQLcl MCP Server Installation and Startup Script
# This script installs and starts the Oracle SQLcl MCP Server

set -e

echo "=========================================="
echo "LibreChat OCI SQL Explorer - SQLcl MCP Server Setup"
echo "=========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm."
    exit 1
fi

echo "npm version: $(npm --version)"

# Install Oracle SQLcl MCP Server if not already installed
if ! command -v sqlcl-mcp-server &> /dev/null; then
    echo "Installing Oracle SQLcl MCP Server..."
    npm install -g @oracle/sqlcl-mcp-server
else
    echo "Oracle SQLcl MCP Server is already installed"
fi

# Check if DB_CONNECTION_STRING is set
if [ -z "$DB_CONNECTION_STRING" ]; then
    echo "Error: DB_CONNECTION_STRING environment variable is not set."
    echo ""
    echo "Please set the database connection string:"
    echo "export DB_CONNECTION_STRING=\"username/password@host:port/service\""
    echo ""
    echo "Example:"
    echo "export DB_CONNECTION_STRING=\"admin/MyPassword123@localhost:1521/FREEPDB1\""
    echo ""
    echo "For Oracle Autonomous Database with wallet:"
    echo "export DB_CONNECTION_STRING=\"admin/MyPassword123@mydb_high\""
    echo "export DB_WALLET_PATH=\"/path/to/wallet\""
    exit 1
fi

# Set default port
SQLCL_MCP_PORT=${SQLCL_MCP_PORT:-3100}

echo "Starting Oracle SQLcl MCP Server..."
echo "Port: $SQLCL_MCP_PORT"
echo "Transport: streamable-http"
echo "Database: ${DB_CONNECTION_STRING%%/*}@..."
echo ""

# Build command with optional wallet path
CMD="sqlcl-mcp-server --port $SQLCL_MCP_PORT --transport streamable-http --connection \"$DB_CONNECTION_STRING\""

if [ -n "$DB_WALLET_PATH" ]; then
    echo "Wallet path: $DB_WALLET_PATH"
    CMD="$CMD --wallet-path \"$DB_WALLET_PATH\""
fi

# Start SQLcl MCP Server
eval $CMD

# Note: This script will run in the foreground. Press Ctrl+C to stop.
