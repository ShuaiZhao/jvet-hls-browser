"""
Simple connection generator using Claude (no embeddings).
Analyzes all parameters offline and saves to JSON.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from anthropic import Anthropic


def load_data(codec='vvc'):
    """Load syntax and semantics data."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data' / codec

    with open(data_dir / 'syntax.json', 'r') as f:
        syntax = json.load(f)

    with open(data_dir / 'semantics.json', 'r') as f:
        semantics = json.load(f)

    return syntax, semantics


def analyze_parameter(client, param_name, param_info, all_params):
    """Use Claude to analyze one parameter's connections."""

    prompt = f"""Analyze this video codec parameter and find its connections to other parameters.

Parameter: {param_name}
Definition: {param_info['definition']}
Section: {param_info['section']}

Other available parameters (first 100):
{', '.join(list(all_params.keys())[:100])}

Identify:
1. **References**: Parameters mentioned in this definition
2. **Dependencies**: Parameters this depends on or that depend on it
3. **Related**: Similar naming patterns or concepts

Return ONLY JSON (no markdown):
{{
  "references": [{{"parameter": "name", "context": "why", "strength": 0.95}}],
  "dependencies": [{{"parameter": "name", "context": "why", "strength": 0.90}}],
  "related": [{{"parameter": "name", "context": "why", "strength": 0.85}}]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()

        # Extract JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()

        analysis = json.loads(text)

        # Format connections
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

        return connections

    except Exception as e:
        print(f"  ⚠️  Error analyzing {param_name}: {e}")
        return {
            'references': [],
            'dependencies': [],
            'related_concepts': []
        }


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate parameter connections using Claude API')
    parser.add_argument('--codec', type=str, default='vvc',
                        choices=['vvc', 'hevc', 'avc'],
                        help='Codec to process (default: vvc)')
    args = parser.parse_args()
    codec = args.codec

    # Check API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-key'")
        return 1

    client = Anthropic(api_key=api_key)

    print(f"=" * 60)
    print(f"Generating connections for {codec.upper()} using Claude")
    print(f"=" * 60)
    print()

    # Load data
    print("Loading data...")
    syntax, semantics = load_data(codec)
    print(f"✓ Loaded {len(semantics)} parameters")
    print()

    # Setup output paths
    output_dir = Path(__file__).parent.parent / 'data' / codec
    output_file = output_dir / 'connections.json'
    checkpoint_file = output_dir / 'connections_checkpoint.json'

    # Check for existing checkpoint and resume if found
    connections = {}
    start_index = 0

    if checkpoint_file.exists():
        print("✓ Found checkpoint file - resuming from previous run")
        with open(checkpoint_file, 'r') as f:
            connections = json.load(f)
        start_index = len(connections)
        print(f"✓ Loaded {start_index} previously analyzed parameters")
        print()

    # Analyze each parameter
    print("Analyzing parameters...")
    print("(This may take a while for large specs)")
    print()

    total = len(semantics)

    for i, (param_name, param_info) in enumerate(semantics.items(), 1):
        # Skip already processed parameters
        if param_name in connections:
            continue

        print(f"[{i}/{total}] Analyzing {param_name}...", end=' ')

        conn = analyze_parameter(client, param_name, param_info, semantics)
        connections[param_name] = conn

        total_connections = len(conn['references']) + len(conn['dependencies']) + len(conn['related_concepts'])
        print(f"✓ Found {total_connections} connections")

        # Save checkpoint every 10 parameters
        if i % 10 == 0 or i == total:
            with open(checkpoint_file, 'w') as f:
                json.dump(connections, f, indent=2)
            print(f"  💾 Checkpoint saved ({i}/{total})")

        # Rate limiting (20 requests per minute for Claude)
        if i < total:
            time.sleep(3)  # 3 seconds between requests

    print()

    # Save final version
    with open(output_file, 'w') as f:
        json.dump(connections, f, indent=2)

    # Remove checkpoint file after successful completion
    if checkpoint_file.exists():
        checkpoint_file.unlink()

    print(f"=" * 60)
    print(f"✓ Saved connections to: {output_file}")
    print(f"=" * 60)
    print()
    print(f"Summary:")
    print(f"  - Parameters analyzed: {len(connections)}")
    print(f"  - Total connections: {sum(len(c['references']) + len(c['dependencies']) + len(c['related_concepts']) for c in connections.values())}")
    print()
    print("Next: Open web/index.html to browse the specification!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
