#!/usr/bin/env python3
"""
Simple proxy server to handle Claude API calls from the browser
This bypasses CORS restrictions for local development
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load API key from config
config_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
        API_KEY = config.get('ANTHROPIC_API_KEY', os.environ.get('ANTHROPIC_API_KEY'))
except FileNotFoundError:
    API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not API_KEY:
    print("Warning: No API key found. Set ANTHROPIC_API_KEY environment variable or create web/config.json")

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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'api_key_configured': bool(API_KEY)})

if __name__ == '__main__':
    print("=" * 60)
    print("Claude API Proxy Server")
    print("=" * 60)
    print(f"API Key configured: {bool(API_KEY)}")
    print("\nStarting server on http://localhost:8001")
    print("Use this in your browser for AI analysis features")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)

    # Production-ready configuration
    app.run(
        host='0.0.0.0',
        port=8001,
        debug=False,  # Disable debug mode for stability
        threaded=True,  # Handle multiple requests
        use_reloader=False  # Prevent auto-restart
    )
