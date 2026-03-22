#!/usr/bin/env python3
"""
Fix semantics_ref fields in syntax.json by matching parameters to semantics.json
"""

import json
import re
from pathlib import Path

def clean_parameter_name(param):
    """Extract clean parameter name from syntax parameter"""
    # Remove function call markers
    param = param.replace('( )', '').replace('()', '').strip()

    # Remove trailing spaces and special characters
    param = param.replace('\u00a0', '').strip()

    # If it's an assignment or expression, extract the variable name
    if '=' in param:
        # Get the part before =
        param = param.split('=')[0].strip()

    # Remove array indices
    param = re.sub(r'\[.*?\]', '', param)

    # Remove trailing parentheses for function calls
    param = param.replace('(', '').replace(')', '').strip()

    return param

def main():
    codec = 'vvc'

    # Load data files
    syntax_path = Path(f'web/data/{codec}/syntax.json')
    semantics_path = Path(f'web/data/{codec}/semantics.json')

    print("=" * 80)
    print("FIXING SEMANTICS REFERENCES IN SYNTAX.JSON")
    print("=" * 80)

    with open(syntax_path) as f:
        syntax = json.load(f)

    with open(semantics_path) as f:
        semantics = json.load(f)

    print(f"\nLoaded {len(syntax)} syntax structures")
    print(f"Loaded {len(semantics)} semantic entries")

    # Fix references
    total_params = 0
    matched = 0
    unmatched = 0

    for struct_name, struct_data in syntax.items():
        parameters = struct_data.get('parameters', [])

        for param in parameters:
            param_name = param.get('name', '')
            param_type = param.get('condition', '')

            # Skip control flow structures
            if param_type in ['other', 'control']:
                continue

            total_params += 1

            # Clean the parameter name
            clean_name = clean_parameter_name(param_name)

            # Check if it exists in semantics
            if clean_name and clean_name in semantics:
                param['semantics_ref'] = clean_name
                matched += 1
            else:
                # Try some variations
                found = False

                # Try without underscores
                if clean_name.replace('_', '') in semantics:
                    param['semantics_ref'] = clean_name.replace('_', '')
                    matched += 1
                    found = True

                # Try with brackets removed (for arrays)
                elif re.sub(r'\[.*?\]', '', param_name).strip() in semantics:
                    ref = re.sub(r'\[.*?\]', '', param_name).strip()
                    param['semantics_ref'] = ref
                    matched += 1
                    found = True

                if not found:
                    param['semantics_ref'] = None
                    unmatched += 1

    print(f"\n{' =' * 40}")
    print("RESULTS")
    print(f"{' =' * 40}")
    print(f"Total parameters processed: {total_params}")
    print(f"Matched: {matched} ({matched*100//total_params if total_params > 0 else 0}%)")
    print(f"Unmatched: {unmatched} ({unmatched*100//total_params if total_params > 0 else 0}%)")

    # Backup original
    backup_path = syntax_path.with_suffix('.json.backup')
    with open(backup_path, 'w') as f:
        with open(syntax_path) as orig:
            f.write(orig.read())
    print(f"\nBackup saved to: {backup_path}")

    # Save updated syntax
    with open(syntax_path, 'w') as f:
        json.dump(syntax, f, indent=2, ensure_ascii=False)

    print(f"Updated syntax saved to: {syntax_path}")
    print(f"\n✅ Done! semantics_ref fields have been populated.")

if __name__ == '__main__':
    main()
