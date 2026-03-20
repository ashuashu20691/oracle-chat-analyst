#!/bin/bash
# LibreChat OCI SQL Explorer - Stop All Services
# This script stops all running services

set -e

echo "=========================================="
echo "LibreChat OCI SQL Explorer - Stop All Services"
echo "=========================================="

# Function to stop a service by PID file
stop_service() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo "Force stopping $service_name..."
                kill -9 $pid
            fi
            
            echo "✓ $service_name stopped"
        else
            echo "✗ $service_name is not running (stale PID file)"
        fi
        rm -f "$pid_file"
    else
        echo "✗ $service_name PID file not found"
    fi
}

# Stop LibreChat frontend
stop_service "logs/librechat-frontend.pid" "LibreChat Frontend"

# Stop LibreChat backend
stop_service "logs/librechat-backend.pid" "LibreChat Backend"

# Stop SQLcl MCP Server
stop_service "logs/sqlcl-mcp.pid" "SQLcl MCP Server"

# Stop LiteLLM
stop_service "logs/litellm.pid" "LiteLLM"

# Additional cleanup - kill any remaining processes by name
echo ""
echo "Performing additional cleanup..."

# Kill any remaining LiteLLM processes
if pgrep -f "litellm.*litellm_config.yaml" > /dev/null; then
    echo "Killing remaining LiteLLM processes..."
    pkill -f "litellm.*litellm_config.yaml"
fi

# Kill any remaining SQLcl MCP processes
if pgrep -f "sqlcl-mcp-server" > /dev/null; then
    echo "Killing remaining SQLcl MCP processes..."
    pkill -f "sqlcl-mcp-server"
fi

# Kill any remaining LibreChat processes
if pgrep -f "npm run backend" > /dev/null; then
    echo "Killing remaining LibreChat backend processes..."
    pkill -f "npm run backend"
fi

if pgrep -f "npm run frontend" > /dev/null; then
    echo "Killing remaining LibreChat frontend processes..."
    pkill -f "npm run frontend"
fi

echo ""
echo "=========================================="
echo "All services stopped"
echo "=========================================="
echo ""
echo "Log files are preserved in logs/ directory"
echo "To start services again, run: ./scripts/start-all.sh"
echo ""
