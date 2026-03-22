#!/bin/bash

# Simple script to start the Interactive HLS server
# Just run: ./RUN_SERVER.sh

cd "$(dirname "$0")"

echo "=========================================="
echo "Interactive HLS Specification Browser"
echo "=========================================="
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo ""
    echo "AI features will be limited without an API key."
    echo "To set it, run:"
    echo "  export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
fi

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
fi

echo "Starting server..."
echo ""

# Start the combined server
python3 server/combined_server.py

echo ""
echo "Server stopped."
