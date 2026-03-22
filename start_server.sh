#!/bin/bash

# Interactive HLS Server Startup Script
# This script starts the Flask proxy server with auto-restart capability

echo "========================================"
echo "Interactive HLS Server Manager"
echo "========================================"
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY environment variable is not set"
    echo "   AI features will not work without an API key"
    echo ""
    echo "   To set it, run:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
fi

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Function to start server with auto-restart
start_server() {
    local server_script=$1
    local server_name=$2

    echo ""
    echo "Starting $server_name..."
    echo "Press CTRL+C to stop"
    echo "----------------------------------------"

    while true; do
        $PYTHON_CMD "$server_script"
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            # Clean exit (CTRL+C)
            echo ""
            echo "Server stopped cleanly"
            break
        else
            # Crashed - restart
            echo ""
            echo "⚠️  Server crashed with exit code $exit_code"
            echo "🔄 Restarting in 3 seconds..."
            echo "   (Press CTRL+C to abort)"
            sleep 3
        fi
    done
}

# Menu to choose which server to run
echo ""
echo "Which server do you want to start?"
echo "1) Combined Server (port 8000) - RECOMMENDED ⭐"
echo "   Serves static files + AI proxy in one server"
echo ""
echo "2) Proxy Server (port 8001) - Legacy"
echo "   For AI analysis features only"
echo ""
echo "3) Backend API Server (port 5000) - Advanced"
echo "   For real-time analysis and search"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        start_server "server/combined_server.py" "Combined Server (Static + AI Proxy)"
        ;;
    2)
        start_server "server/proxy.py" "Proxy Server"
        ;;
    3)
        start_server "web/backend/api_server.py" "Backend API Server"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Server stopped"
echo "========================================"
