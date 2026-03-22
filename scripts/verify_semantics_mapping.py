#!/usr/bin/env python3
"""
Verify that all syntax parameters have correct semantics mappings
"""

import json
import re
from collections import defaultdict

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
    # Load data files
    with open('web/data/vvc/syntax.json') as f:
        syntax = json.load(f)

    with open('web/data/vvc/semantics.json') as f:
        semantics = json.load(f)

    print("=" * 80)
    print("SEMANTICS MAPPING VERIFICATION")
    print("=" * 80)
    print(f"\nSyntax structures: {len(syntax)}")
    print(f"Semantic entries: {len(semantics)}")

    # Collect all parameters from syntax structures
    all_params = {}  # param_name -> list of (syntax_struct, original_name)

    for struct_name, struct_data in syntax.items():
        parameters = struct_data.get('parameters', [])

        for param in parameters:
            param_name = param.get('name', '')
            param_type = param.get('condition', '')

            # Skip control flow structures
            if param_type in ['other', 'control']:
                continue

            # Clean the parameter name
            clean_name = clean_parameter_name(param_name)

            if clean_name:
                if clean_name not in all_params:
                    all_params[clean_name] = []
                all_params[clean_name].append((struct_name, param_name))

    print(f"\nTotal unique parameters found: {len(all_params)}")

    # Check mappings
    mapped = []
    unmapped = []

    for param_name in sorted(all_params.keys()):
        if param_name in semantics:
            mapped.append(param_name)
        else:
            unmapped.append((param_name, all_params[param_name]))

    print(f"\n{'=' * 80}")
    print(f"MAPPED PARAMETERS: {len(mapped)}/{len(all_params)}")
    print(f"{'=' * 80}")

    print(f"\n{'=' * 80}")
    print(f"UNMAPPED PARAMETERS: {len(unmapped)}")
    print(f"{'=' * 80}")

    if unmapped:
        print("\nParameters without semantics:")
        for param_name, occurrences in unmapped[:50]:  # Show first 50
            print(f"\n  Parameter: '{param_name}'")
            for struct, orig_name in occurrences[:3]:  # Show first 3 occurrences
                print(f"    - Found in: {struct} (original: '{orig_name}')")

    # Check for potential mismatches
    print(f"\n{'=' * 80}")
    print("CHECKING FOR POTENTIAL MISMATCHES")
    print(f"{'=' * 80}")

    mismatches = []
    for param_name, occurrences in unmapped:
        # Check if there's a similar name in semantics
        similar = []
        for sem_key in semantics.keys():
            # Case-insensitive partial match
            if param_name.lower() in sem_key.lower() or sem_key.lower() in param_name.lower():
                similar.append(sem_key)

        if similar:
            mismatches.append((param_name, similar, occurrences))

    if mismatches:
        print(f"\nFound {len(mismatches)} potential mismatches:")
        for param_name, similar, occurrences in mismatches[:20]:  # Show first 20
            print(f"\n  '{param_name}' might match:")
            for sim in similar[:3]:
                print(f"    -> '{sim}'")
            print(f"    Used in: {occurrences[0][0]}")

    # Verify semantic references in syntax.json
    print(f"\n{'=' * 80}")
    print("CHECKING semantics_ref FIELDS")
    print(f"{'=' * 80}")

    total_params = 0
    ref_set = 0
    ref_null = 0
    ref_correct = 0
    ref_incorrect = []

    for struct_name, struct_data in syntax.items():
        parameters = struct_data.get('parameters', [])

        for param in parameters:
            param_name = param.get('name', '')
            semantics_ref = param.get('semantics_ref')
            param_type = param.get('condition', '')

            # Skip control flow
            if param_type in ['other', 'control']:
                continue

            total_params += 1

            if semantics_ref:
                ref_set += 1
                # Check if ref exists in semantics
                if semantics_ref in semantics:
                    ref_correct += 1
                else:
                    ref_incorrect.append((struct_name, param_name, semantics_ref))
            else:
                ref_null += 1

    print(f"\nTotal parameters: {total_params}")
    print(f"  semantics_ref set: {ref_set}")
    print(f"  semantics_ref null: {ref_null}")
    print(f"  Correct references: {ref_correct}")
    print(f"  Incorrect references: {len(ref_incorrect)}")

    if ref_incorrect:
        print(f"\nIncorrect semantics_ref values:")
        for struct, param, ref in ref_incorrect[:20]:
            print(f"  {struct}: '{param}' -> '{ref}' (NOT FOUND)")

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Coverage: {len(mapped)}/{len(all_params)} ({len(mapped)*100//len(all_params)}%)")
    print(f"Unmapped: {len(unmapped)}")
    print(f"Potential mismatches: {len(mismatches)}")
    print(f"Incorrect semantics_ref: {len(ref_incorrect)}")

    if len(unmapped) > 0 or len(ref_incorrect) > 0:
        print(f"\n⚠️  ACTION REQUIRED: Fix mapping issues")
    else:
        print(f"\n✅  All mappings are correct!")

    # Save report
    report = {
        'total_syntax_structures': len(syntax),
        'total_semantic_entries': len(semantics),
        'total_unique_parameters': len(all_params),
        'mapped_parameters': len(mapped),
        'unmapped_parameters': len(unmapped),
        'potential_mismatches': len(mismatches),
        'incorrect_refs': len(ref_incorrect),
        'unmapped_list': [
            {
                'parameter': param,
                'occurrences': [
                    {'syntax_structure': struct, 'original_name': orig}
                    for struct, orig in occ
                ]
            }
            for param, occ in unmapped
        ],
        'incorrect_refs_list': [
            {
                'syntax_structure': struct,
                'parameter': param,
                'incorrect_ref': ref
            }
            for struct, param, ref in ref_incorrect
        ]
    }

    with open('semantics_mapping_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: semantics_mapping_report.json")

if __name__ == '__main__':
    main()
