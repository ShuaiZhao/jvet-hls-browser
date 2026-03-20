"""
Real-time Claude API server for connection analysis.
This approach skips embedding generation and uses Claude on-demand.
"""

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic

app = Flask(__name__)
CORS(app)

# Initialize Claude client
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY not set!")

client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Load codec data
DATA_DIR = Path(__file__).parent.parent.parent / 'data'
codec_data = {}


def load_codec_data(codec='vvc'):
    """Load syntax and semantics data for a codec."""
    if codec in codec_data:
        return codec_data[codec]

    codec_path = DATA_DIR / codec
    data = {
        'syntax': {},
        'semantics': {}
    }

    # Load syntax
    syntax_file = codec_path / 'syntax.json'
    if syntax_file.exists():
        with open(syntax_file, 'r') as f:
            data['syntax'] = json.load(f)

    # Load semantics
    semantics_file = codec_path / 'semantics.json'
    if semantics_file.exists():
        with open(semantics_file, 'r') as f:
            data['semantics'] = json.load(f)

    codec_data[codec] = data
    return data


@app.route('/api/analyze-parameter', methods=['POST'])
def analyze_parameter():
    """Analyze a parameter using Claude in real-time."""
    if not client:
        return jsonify({'error': 'Claude API not configured'}), 500

    data = request.json
    codec = data.get('codec', 'vvc')
    param_name = data.get('parameter')

    if not param_name:
        return jsonify({'error': 'Parameter name required'}), 400

    # Load codec data
    codec_info = load_codec_data(codec)

    if param_name not in codec_info['semantics']:
        return jsonify({'error': 'Parameter not found'}), 404

    param_info = codec_info['semantics'][param_name]

    # Build prompt for Claude
    prompt = f"""You are analyzing the H.266/VVC video codec specification.

Analyze this syntax parameter and identify its relationships with other parameters:

**Parameter:** {param_name}
**Definition:** {param_info['definition']}
**Section:** {param_info['section']}

**Available parameters in the specification:**
{', '.join(list(codec_info['semantics'].keys())[:100])}

Please identify:
1. **Direct References**: Parameters that this parameter directly references or is referenced by
2. **Dependencies**: Parameters that this depends on (conditional presence, derivations)
3. **Related Concepts**: Parameters with similar purposes

For each relationship, provide:
- Parameter name (must be from the available parameters list)
- Relationship type
- Brief context
- Confidence score (0.0-1.0)

Return ONLY valid JSON (no markdown):
{{
  "references": [
    {{"parameter": "...", "context": "...", "strength": 0.95}}
  ],
  "dependencies": [
    {{"parameter": "...", "context": "...", "strength": 0.90}}
  ],
  "related": [
    {{"parameter": "...", "context": "...", "strength": 0.85}}
  ]
}}"""

    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        response_text = response.content[0].text.strip()

        # Extract JSON from response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        analysis = json.loads(response_text)

        # Format for frontend
        connections = {
            'references': [
                {
                    'parameter': r['parameter'],
                    'type': 'referenced_by',
                    'context': r['context'],
                    'strength': r['strength']
                }
                for r in analysis.get('references', [])
            ],
            'dependencies': [
                {
                    'parameter': d['parameter'],
                    'type': 'dependency',
                    'context': d['context'],
                    'strength': d['strength']
                }
                for d in analysis.get('dependencies', [])
            ],
            'related_concepts': [
                {
                    'parameter': r['parameter'],
                    'type': 'related',
                    'context': r['context'],
                    'strength': r['strength']
                }
                for r in analysis.get('related', [])
            ]
        }

        return jsonify({
            'parameter': param_name,
            'connections': connections,
            'analyzed_at': 'realtime'
        })

    except Exception as e:
        print(f"Error analyzing parameter: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def semantic_search():
    """Search for parameters using Claude."""
    if not client:
        return jsonify({'error': 'Claude API not configured'}), 500

    data = request.json
    codec = data.get('codec', 'vvc')
    query = data.get('query')

    if not query:
        return jsonify({'error': 'Query required'}), 400

    # Load codec data
    codec_info = load_codec_data(codec)

    # Build search prompt
    prompt = f"""You are searching the H.266/VVC video codec specification.

User query: "{query}"

Available parameters:
{json.dumps(codec_info['semantics'], indent=2)[:5000]}

Find the top 5 most relevant parameters that match the user's query.

Return ONLY valid JSON (no markdown):
{{
  "results": [
    {{
      "parameter": "parameter_name",
      "relevance": 0.95,
      "reason": "why it matches the query"
    }}
  ]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = response.content[0].text.strip()

        # Extract JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        results = json.loads(response_text)

        return jsonify(results)

    except Exception as e:
        print(f"Error searching: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'claude_configured': client is not None
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Interactive HLS API Server")
    print("=" * 60)
    print(f"Claude API configured: {client is not None}")
    print(f"Data directory: {DATA_DIR}")
    print()
    print("Starting server on http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, port=5000)
