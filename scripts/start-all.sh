#!/bin/bash
# LibreChat OCI SQL Explorer - Start All Services
# This script starts all required services in the background

set -e

echo "=========================================="
echo "LibreChat OCI SQL Explorer - Start All Services"
echo "=========================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found."
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
echo "Loading environment variables from .env..."
export $(grep -v '^#' .env | xargs)

# Create logs directory
mkdir -p logs

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo "Waiting for $name to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✓ $name is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo "✗ $name failed to start within timeout"
    return 1
}

# Check if services are already running
if check_port 4000; then
    echo "Warning: Port 4000 is already in use (LiteLLM may be running)"
fi

if check_port 3100; then
    echo "Warning: Port 3100 is already in use (SQLcl MCP may be running)"
fi

if check_port 3080; then
    echo "Warning: Port 3080 is already in use (LibreChat may be running)"
fi

echo ""
echo "Starting services..."
echo ""

# Start LiteLLM
echo "1. Starting LiteLLM..."
if ! check_port 4000; then
    nohup litellm --config litellm_config.yaml --port ${LITELLM_PORT:-4000} > logs/litellm.log 2>&1 &
    LITELLM_PID=$!
    echo "   PID: $LITELLM_PID"
    echo $LITELLM_PID > logs/litellm.pid
    wait_for_service "http://localhost:4000/health" "LiteLLM"
else
    echo "   Already running"
fi

echo ""

# Start SQLcl MCP Server
echo "2. Starting SQLcl MCP Server..."
if ! check_port 3100; then
    if [ -n "$DB_WALLET_PATH" ]; then
        nohup sqlcl-mcp-server --port ${SQLCL_MCP_PORT:-3100} --transport streamable-http \
            --connection "$DB_CONNECTION_STRING" --wallet-path "$DB_WALLET_PATH" \
            > logs/sqlcl-mcp.log 2>&1 &
    else
        nohup sqlcl-mcp-server --port ${SQLCL_MCP_PORT:-3100} --transport streamable-http \
            --connection "$DB_CONNECTION_STRING" > logs/sqlcl-mcp.log 2>&1 &
    fi
    SQLCL_PID=$!
    echo "   PID: $SQLCL_PID"
    echo $SQLCL_PID > logs/sqlcl-mcp.pid
    wait_for_service "http://localhost:3100/health" "SQLcl MCP Server"
else
    echo "   Already running"
fi

echo ""

# Start LibreChat
echo "3. Starting LibreChat..."
if ! check_port 3080; then
    cd LibreChat
    
    # Start backend
    nohup npm run backend > ../logs/librechat-backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    echo $BACKEND_PID > ../logs/librechat-backend.pid
    
    # Wait a few seconds for backend to initialize
    sleep 5
    
    # Start frontend
    nohup npm run frontend > ../logs/librechat-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
    echo $FRONTEND_PID > ../logs/librechat-frontend.pid
    
    cd ..
    
    wait_for_service "http://localhost:3080" "LibreChat"
else
    echo "   Already running"
fi

echo ""
echo "=========================================="
echo "All services started successfully!"
echo "=========================================="
echo ""
echo "Service Status:"
echo "  - LiteLLM:         http://localhost:4000"
echo "  - SQLcl MCP:       http://localhost:3100"
echo "  - LibreChat:       http://localhost:3080"
echo ""
echo "Logs are available in the logs/ directory:"
echo "  - logs/litellm.log"
echo "  - logs/sqlcl-mcp.log"
echo "  - logs/librechat-backend.log"
echo "  - logs/librechat-frontend.log"
echo ""
echo "To stop all services, run: ./scripts/stop-all.sh"
echo ""
echo "Open your browser to: http://localhost:3080"
echo ""
