#!/bin/bash

# Interactive HLS Setup Script

echo "===================================================="
echo " Interactive HLS Specification Browser - Setup"
echo "===================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set!"
    echo ""
    echo "Please set your Claude API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Get an API key at: https://console.anthropic.com/"
    echo ""
else
    echo "✓ ANTHROPIC_API_KEY is set"
    echo ""
fi

# Check for spec file
spec_file="../H266_VVC/H266-VVC-v3.docx"
if [ -f "$spec_file" ]; then
    echo "✓ VVC specification found: $spec_file"
    echo ""

    # Ask to process
    read -p "Process VVC specification now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Processing VVC specification..."
        python3 scripts/process_spec.py --codec vvc --skip-ai
        echo ""
        echo "✓ VVC specification processed!"
        echo ""
    fi
else
    echo "⚠️  VVC specification not found at: $spec_file"
    echo "   Make sure the file exists or update the path in codec_config.yaml"
    echo ""
fi

echo "===================================================="
echo " Setup Complete!"
echo "===================================================="
echo ""
echo "Next steps:"
echo "  1. Set your API key (if not done):"
echo "     export ANTHROPIC_API_KEY='your-key'"
echo ""
echo "  2. Start the API server:"
echo "     cd web/backend"
echo "     python3 api_server.py"
echo ""
echo "  3. Open web/index.html in your browser"
echo ""
echo "Or use a local web server:"
echo "     cd web"
echo "     python3 -m http.server 8000"
echo "     # Then open http://localhost:8000"
echo ""
