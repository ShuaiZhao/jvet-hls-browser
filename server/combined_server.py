#!/usr/bin/env python3
"""
Combined server that serves both static files and handles Claude API proxy
This eliminates the need for running multiple servers
Runs on port 8000
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import anthropic
import os
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the project root directory
BASE_DIR = Path(__file__).parent.parent
WEB_DIR = BASE_DIR / 'web'

# Load API key from config or environment
config_path = WEB_DIR / 'config.json'
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        API_KEY = config.get('anthropic_api_key') or config.get('ANTHROPIC_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
except FileNotFoundError:
    API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not API_KEY:
    print("⚠️  Warning: No API key found. Set ANTHROPIC_API_KEY environment variable or create web/config.json")
    print("   AI features will not work without an API key")

# ============================================================================
# API Endpoints (Claude Proxy)
# ============================================================================

@app.route('/api/claude', methods=['POST', 'OPTIONS'])
def claude_proxy():
    """Proxy endpoint for Claude API calls"""
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204

    if not API_KEY:
        return jsonify({'error': 'API key not configured'}), 500

    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract request parameters
        model = data.get('model', 'claude-sonnet-4-5-20250929')
        max_tokens = data.get('max_tokens', 1024)
        messages = data.get('messages', [])

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Call Claude API with timeout handling
        client = anthropic.Anthropic(
            api_key=API_KEY,
            timeout=60.0  # 60 second timeout
        )
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages
        )

        # Return response in same format as API
        return jsonify({
            'content': [{'text': message.content[0].text}],
            'model': message.model,
            'stop_reason': message.stop_reason
        })

    except anthropic.APITimeoutError as e:
        print(f"Claude API timeout: {e}")
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except anthropic.APIError as e:
        print(f"Claude API error: {e}")
        return jsonify({'error': f'Claude API error: {str(e)}'}), 502
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'api_key_configured': bool(API_KEY),
        'static_files': str(WEB_DIR),
        'server_type': 'combined'
    })


# ============================================================================
# Static File Serving
# ============================================================================

@app.route('/')
def index():
    """Serve the login page as default"""
    return send_file(WEB_DIR / 'login.html')


@app.route('/index.html')
def main_app():
    """Serve the main application"""
    return send_file(WEB_DIR / 'index.html')


@app.route('/login.html')
def login():
    """Serve the login page"""
    return send_file(WEB_DIR / 'login.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from web directory"""
    try:
        return send_from_directory(WEB_DIR, path)
    except FileNotFoundError:
        # Try to serve as directory index
        dir_path = WEB_DIR / path
        if dir_path.is_dir():
            index_file = dir_path / 'index.html'
            if index_file.exists():
                return send_file(index_file)
        return jsonify({'error': 'File not found'}), 404


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Interactive HLS Combined Server")
    print("=" * 60)
    print(f"✓ API Key configured: {bool(API_KEY)}")
    print(f"✓ Static files: {WEB_DIR}")
    print()
    print("Services:")
    print("  • Static web files (HTML/CSS/JS)")
    print("  • Claude API proxy (/api/claude)")
    print()
    print("Starting server on http://localhost:8000")
    print()
    print("Open in browser: http://localhost:8000")
    print("Press CTRL+C to stop the server")
    print("=" * 60)

    # Production-ready configuration
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,  # Disable debug mode for stability
        threaded=True,  # Handle multiple requests
        use_reloader=False  # Prevent auto-restart
    )
