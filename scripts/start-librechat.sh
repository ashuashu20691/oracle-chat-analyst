#!/bin/bash
# LibreChat OCI SQL Explorer - LibreChat Configuration and Startup Script
# This script configures and starts LibreChat

set -e

echo "=========================================="
echo "LibreChat OCI SQL Explorer - LibreChat Setup"
echo "=========================================="

# Check if we're in the LibreChat directory or project root
if [ -d "LibreChat" ]; then
    echo "Detected project root directory"
    LIBRECHAT_DIR="LibreChat"
elif [ -f "package.json" ] && grep -q "librechat" package.json; then
    echo "Detected LibreChat directory"
    LIBRECHAT_DIR="."
else
    echo "Error: LibreChat directory not found."
    echo "Please run this script from the project root or LibreChat directory."
    exit 1
fi

cd "$LIBRECHAT_DIR"

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

# Check if librechat.yaml exists
if [ ! -f "librechat.yaml" ]; then
    echo "Error: librechat.yaml not found in LibreChat directory."
    echo "Please ensure the configuration file is present."
    exit 1
fi

echo "Found librechat.yaml configuration"

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
        echo ""
        echo "IMPORTANT: Please edit .env file and configure required variables:"
        echo "  - MONGO_URI (MongoDB connection string)"
        echo "  - LITELLM_MASTER_KEY (from LiteLLM setup)"
        echo ""
        read -p "Press Enter to continue after configuring .env..."
    else
        echo "Error: .env file not found and .env.example is missing."
        exit 1
    fi
fi

# Check if LITELLM_MASTER_KEY is set in environment or .env
if [ -z "$LITELLM_MASTER_KEY" ]; then
    if grep -q "LITELLM_MASTER_KEY" .env; then
        echo "Loading LITELLM_MASTER_KEY from .env file"
        export $(grep LITELLM_MASTER_KEY .env | xargs)
    else
        echo "Warning: LITELLM_MASTER_KEY not found in environment or .env file."
        echo "Please ensure it matches the key used in LiteLLM setup."
    fi
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
else
    echo "Dependencies already installed"
fi

# Verify configuration
echo ""
echo "Verifying configuration..."
echo "  - Artifacts enabled: $(grep -A 1 'artifacts:' librechat.yaml | grep 'enabled' || echo 'Not found')"
echo "  - SQL Explorer Agent: $(grep 'SQL Explorer Agent' librechat.yaml && echo 'Found' || echo 'Not found')"
echo "  - MCP Server configured: $(grep 'oracle-sqlcl' librechat.yaml && echo 'Found' || echo 'Not found')"
echo ""

# Check if LiteLLM is running
if ! curl -s http://localhost:4000/health > /dev/null 2>&1; then
    echo "Warning: LiteLLM proxy is not responding at http://localhost:4000"
    echo "Please ensure LiteLLM is running (use scripts/start-litellm.sh)"
    echo ""
fi

# Check if SQLcl MCP Server is running
if ! curl -s http://localhost:3100/mcp > /dev/null 2>&1; then
    echo "Warning: SQLcl MCP Server is not responding at http://localhost:3100"
    echo "Please ensure SQLcl MCP Server is running (use scripts/start-sqlcl-mcp.sh)"
    echo ""
fi

echo "Starting LibreChat..."
echo "Frontend will be available at: http://localhost:3080"
echo ""

# Start LibreChat (both backend and frontend)
npm run backend &
BACKEND_PID=$!

# Wait a few seconds for backend to start
sleep 5

npm run frontend &
FRONTEND_PID=$!

echo ""
echo "LibreChat is starting..."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
