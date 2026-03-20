"""
Main script to process video codec specifications.
Extracts syntax, semantics, and generates connections.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.vvc import VVCParser
from scripts.generate_connections import ConnectionAnalyzer


def load_config(codec: str) -> dict:
    """Load codec configuration from YAML file."""
    config_path = Path(__file__).parent.parent / 'config' / 'codec_config.yaml'

    with open(config_path, 'r') as f:
        all_config = yaml.safe_load(f)

    if codec not in all_config:
        raise ValueError(f"Unknown codec: {codec}. Available: {list(all_config.keys())}")

    # Merge codec config with AI and connection patterns config
    codec_config = all_config[codec]
    codec_config['ai'] = all_config.get('ai', {})
    codec_config['connection_patterns'] = all_config.get('connection_patterns', {})

    return codec_config


def get_parser(codec: str, config: dict):
    """Get appropriate parser for the codec."""
    if codec == 'vvc':
        return VVCParser(config)
    elif codec == 'hevc':
        # TODO: Implement HEVC parser
        raise NotImplementedError("HEVC parser not yet implemented")
    elif codec == 'avc':
        # TODO: Implement AVC parser
        raise NotImplementedError("AVC parser not yet implemented")
    else:
        raise ValueError(f"Unknown codec: {codec}")


def export_json(data: dict, output_path: Path) -> None:
    """Export data to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Process video codec HLS specifications'
    )
    parser.add_argument(
        '--codec',
        type=str,
        required=True,
        choices=['vvc', 'hevc', 'avc'],
        help='Codec type to process'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input DOCX file (overrides config)'
    )
    parser.add_argument(
        '--skip-ai',
        action='store_true',
        help='Skip AI connection analysis (faster)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (overrides config)'
    )

    args = parser.parse_args()

    # Load configuration
    print(f"Loading configuration for {args.codec.upper()}...")
    config = load_config(args.codec)

    # Determine input file
    input_file = args.input if args.input else config['spec_file']
    input_path = Path(__file__).parent.parent / input_file

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    # Determine output directory
    output_dir = args.output_dir if args.output_dir else config['output_dir']
    output_path = Path(__file__).parent.parent / output_dir

    print(f"Input file: {input_path}")
    print(f"Output directory: {output_path}")
    print()

    # Initialize parser
    print(f"Initializing {args.codec.upper()} parser...")
    spec_parser = get_parser(args.codec, config)

    # Load document
    spec_parser.load_document(str(input_path))
    print()

    # Parse specification
    print("=" * 60)
    print("PHASE 1: EXTRACTING SYNTAX AND SEMANTICS")
    print("=" * 60)
    syntax_structures, semantics = spec_parser.parse()
    print()

    # Convert to dictionaries
    syntax_dict, semantics_dict = spec_parser.to_dict()

    # Export syntax and semantics
    export_json(syntax_dict, output_path / 'syntax.json')
    export_json(semantics_dict, output_path / 'semantics.json')
    print()

    # Generate connections if not skipped
    if not args.skip_ai:
        print("=" * 60)
        print("PHASE 2: GENERATING AI CONNECTIONS")
        print("=" * 60)

        # Get OpenAI API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Skipping AI connection analysis.")
            print("Set it with: export OPENAI_API_KEY='your-key'")
        else:
            analyzer = ConnectionAnalyzer(config, api_key)
            connections = analyzer.analyze(syntax_structures, semantics)

            # Convert connections to serializable format
            connections_dict = {}
            for param, conns in connections.items():
                connections_dict[param] = {
                    'references': conns['references'],
                    'dependencies': conns['dependencies'],
                    'related_concepts': conns['related_concepts']
                }

            export_json(connections_dict, output_path / 'connections.json')
        print()

    # Generate summary
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Codec: {config['name']}")
    print(f"Syntax structures: {len(syntax_dict)}")
    print(f"Semantic definitions: {len(semantics_dict)}")
    if not args.skip_ai and api_key:
        print(f"Parameter connections: {len(connections_dict)}")
    print()
    print(f"Output files:")
    print(f"  - {output_path / 'syntax.json'}")
    print(f"  - {output_path / 'semantics.json'}")
    if not args.skip_ai and api_key:
        print(f"  - {output_path / 'connections.json'}")
    print()
    print("Next steps:")
    print("  1. Review the generated JSON files")
    print("  2. Open web/index.html to view the interactive browser")
    print("  3. Deploy to GitHub Pages for public access")

    return 0


if __name__ == '__main__':
    sys.exit(main())
