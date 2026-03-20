#!/bin/bash
# LibreChat OCI SQL Explorer - LiteLLM Installation and Startup Script
# This script installs and starts the LiteLLM proxy for OCI GenAI

set -e

echo "=========================================="
echo "LibreChat OCI SQL Explorer - LiteLLM Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

# Install LiteLLM if not already installed
if ! command -v litellm &> /dev/null; then
    echo "Installing LiteLLM..."
    pip3 install litellm
else
    echo "LiteLLM is already installed: $(litellm --version)"
fi

# Check if litellm_config.yaml exists
if [ ! -f "litellm_config.yaml" ]; then
    echo "Error: litellm_config.yaml not found in current directory."
    echo "Please ensure you are running this script from the project root."
    exit 1
fi

# Check if LITELLM_MASTER_KEY is set
if [ -z "$LITELLM_MASTER_KEY" ]; then
    echo "Warning: LITELLM_MASTER_KEY environment variable is not set."
    echo "Generating a random master key..."
    export LITELLM_MASTER_KEY="sk-$(openssl rand -hex 16)"
    echo "Generated LITELLM_MASTER_KEY: $LITELLM_MASTER_KEY"
    echo ""
    echo "IMPORTANT: Save this key! Add it to your .env file:"
    echo "export LITELLM_MASTER_KEY=\"$LITELLM_MASTER_KEY\""
    echo ""
fi

# Check OCI configuration
if [ ! -f "$HOME/.oci/config" ]; then
    echo "Warning: OCI config file not found at ~/.oci/config"
    echo "Please ensure you have configured OCI CLI or provide manual credentials in litellm_config.yaml"
    echo ""
fi

# Set default port
LITELLM_PORT=${LITELLM_PORT:-4000}

echo "Starting LiteLLM proxy..."
echo "Configuration file: litellm_config.yaml"
echo "Port: $LITELLM_PORT"
echo "Master Key: ${LITELLM_MASTER_KEY:0:10}..."
echo ""

# Start LiteLLM
litellm --config litellm_config.yaml --port $LITELLM_PORT

# Note: This script will run in the foreground. Press Ctrl+C to stop.
