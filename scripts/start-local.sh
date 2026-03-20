#!/bin/bash
# LibreChat OCI SQL Explorer - Start All Services Locally
# This script starts all services for local development

set -e

echo "=========================================="
echo "LibreChat OCI SQL Explorer - Local Setup"
echo "=========================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found."
    echo "Creating .env file..."
    cp .env.example .env 2>/dev/null || echo "Note: .env.example not found, using defaults"
fi

# Generate LITELLM_MASTER_KEY first
echo "Checking LITELLM_MASTER_KEY..."
LITELLM_MASTER_KEY=$(grep "^LITELLM_MASTER_KEY=" .env 2>/dev/null | cut -d'=' -f2)

if [ -z "$LITELLM_MASTER_KEY" ]; then
    echo "Generating LITELLM_MASTER_KEY..."
    LITELLM_MASTER_KEY="sk-$(openssl rand -hex 16)"
    # Update .env file
    if grep -q "^LITELLM_MASTER_KEY=" .env; then
        sed -i.bak "s|^LITELLM_MASTER_KEY=.*|LITELLM_MASTER_KEY=$LITELLM_MASTER_KEY|" .env
    else
        echo "LITELLM_MASTER_KEY=$LITELLM_MASTER_KEY" >> .env
    fi
    echo "✓ Generated and saved LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY:0:15}..."
fi

# Load environment variables
echo "Loading environment variables..."
set -a
source .env
set +a

# Create logs directory
mkdir -p logs

echo ""
echo "Prerequisites Check:"
echo "===================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found"
    exit 1
fi
echo "✓ Python: $(python3 --version)"

# Check Python 3.12 (required for LiteLLM)
if ! command -v python3.12 &> /dev/null; then
    echo "⚠ Python 3.12 not found (required for LiteLLM)"
    echo "  Installing Python 3.12 with Homebrew..."
    brew install python@3.12
fi
echo "✓ Python 3.12: $(python3.12 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found"
    exit 1
fi
echo "✓ Node.js: $(node --version)"

# Check MongoDB
if ! pgrep -x mongod > /dev/null; then
    echo "⚠ MongoDB not running. Starting MongoDB..."
    mongod --fork --logpath logs/mongodb.log --dbpath ./data/db 2>/dev/null || echo "Note: Start MongoDB manually if needed"
fi

# Check SQLcl
if [ ! -f "$SQLCL_PATH" ]; then
    echo "✗ SQLcl not found at: $SQLCL_PATH"
    echo "Please update SQLCL_PATH in .env"
    exit 1
fi
echo "✓ SQLcl found at: $SQLCL_PATH"

# Check OCI config
if [ ! -f "$HOME/.oci/config" ]; then
    echo "⚠ OCI config not found at ~/.oci/config"
    echo "Please configure OCI CLI or ensure credentials are set"
fi

echo ""
echo "Starting Services:"
echo "=================="

# Install LiteLLM if needed
if ! command -v litellm &> /dev/null; then
    echo "Installing LiteLLM..."
    
    # Check if Python 3.12 is available (required for uvloop compatibility)
    if ! command -v python3.12 &> /dev/null; then
        echo "⚠ Python 3.12 not found. Installing with Homebrew..."
        brew install python@3.12
    fi
    
    # Check if pipx is available (recommended)
    if command -v pipx &> /dev/null; then
        echo "Using pipx to install LiteLLM with Python 3.12..."
        pipx install --python python3.12 'litellm[proxy]'
        pipx ensurepath
    else
        echo "pipx not found. Installing pipx first..."
        brew install pipx
        pipx ensurepath
        
        echo "Installing LiteLLM with pipx using Python 3.12..."
        pipx install --python python3.12 'litellm[proxy]'
        
        echo ""
        echo "✓ LiteLLM installed successfully"
        echo ""
    fi
    
    # Add pipx bin to PATH
    export PATH="$HOME/.local/bin:$PATH"
fi

# Ensure litellm is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Start LiteLLM in background
echo "1. Starting LiteLLM..."
nohup litellm --config litellm_config.yaml --port ${LITELLM_PORT:-4000} > logs/litellm.log 2>&1 &
LITELLM_PID=$!
echo "   PID: $LITELLM_PID"
echo $LITELLM_PID > logs/litellm.pid

# Wait for LiteLLM to start
echo "   Waiting for LiteLLM to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:4000/health > /dev/null 2>&1; then
        echo "   ✓ LiteLLM is ready"
        break
    fi
    sleep 1
done

echo ""
echo "2. SQLcl MCP Server (stdio mode)"
echo "   ✓ Configured in librechat.yaml"
echo "   ✓ Will be started by LibreChat automatically"
echo "   Path: $SQLCL_PATH"

echo ""
echo "3. Starting LibreChat..."
cd LibreChat

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm ci
else
    echo "   Dependencies already installed"
fi

# Build packages if needed
if [ ! -d "packages/data-schemas/dist" ]; then
    echo "   Building LibreChat packages..."
    npm run build:packages
else
    echo "   Packages already built"
fi

# Copy librechat.yaml if not in LibreChat directory
if [ ! -f "librechat.yaml" ]; then
    echo "   Copying librechat.yaml..."
    cp ../LibreChat/librechat.yaml . 2>/dev/null || echo "   Note: librechat.yaml already in place"
fi

# Create .env for LibreChat if needed
if [ ! -f ".env" ]; then
    echo "   Creating LibreChat .env..."
    cat > .env << EOF
MONGO_URI=${MONGO_URI:-mongodb://127.0.0.1:27017/LibreChat}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-3080}
LITELLM_MASTER_KEY=$LITELLM_MASTER_KEY
NODE_ENV=${NODE_ENV:-development}
JWT_SECRET=${JWT_SECRET:-your-secret-jwt-key-change-this-in-production}
JWT_REFRESH_SECRET=${JWT_REFRESH_SECRET:-your-refresh-secret-jwt-key-change-this-in-production}
EOF
fi

# Start backend
echo "   Starting backend..."
nohup npm run backend > ../logs/librechat-backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo $BACKEND_PID > ../logs/librechat-backend.pid

# Wait for backend
sleep 10

# Start frontend
echo "   Starting frontend..."
nohup npm run frontend > ../logs/librechat-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo $FRONTEND_PID > ../logs/librechat-frontend.pid

cd ..

# Wait for LibreChat to be ready
echo "   Waiting for LibreChat to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:3080 > /dev/null 2>&1; then
        echo "   ✓ LibreChat is ready"
        break
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo "All services started successfully!"
echo "=========================================="
echo ""
echo "Service Status:"
echo "  - LiteLLM:         http://localhost:4000"
echo "  - LibreChat:       http://localhost:3080"
echo "  - SQLcl MCP:       stdio mode (managed by LibreChat)"
echo ""
echo "Configuration:"
echo "  - Model:           google.gemini-2.5-flash"
echo "  - Compartment:     ${OCI_COMPARTMENT_ID:0:30}..."
echo "  - SQLcl Path:      $SQLCL_PATH"
echo ""
echo "Logs:"
echo "  - LiteLLM:         logs/litellm.log"
echo "  - LibreChat:       logs/librechat-backend.log"
echo "  - LibreChat:       logs/librechat-frontend.log"
echo ""
echo "To view logs:"
echo "  tail -f logs/litellm.log"
echo "  tail -f logs/librechat-backend.log"
echo ""
echo "To stop all services:"
echo "  ./scripts/stop-all.sh"
echo ""
echo "Open your browser to: http://localhost:3080"
echo ""
