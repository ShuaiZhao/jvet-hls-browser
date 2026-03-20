#!/usr/bin/env python3
"""
Extract missing semantics using Claude AI to intelligently find definitions
"""

import json
import os
import time
from docx import Document
from pathlib import Path
import anthropic

# Paths
SPEC_PATH = "/Users/shzhao/Library/CloudStorage/GoogleDrive-dr.shuai.zhao@gmail.com/My Drive/JVET/HLS/JVET_notes/codec_specification/H266_VVC/T-REC-H.266-202309-I!!MSW-E v3.docx"
SYNTAX_JSON = "data/vvc/syntax.json"
SEMANTICS_JSON = "data/vvc/semantics.json"
OUTPUT_JSON = "data/vvc/semantics.json"

def load_existing_semantics():
    """Load existing semantics JSON"""
    with open(SEMANTICS_JSON, 'r') as f:
        return json.load(f)

def get_missing_parameters():
    """Get list of parameters in syntax but not in semantics"""
    with open(SYNTAX_JSON, 'r') as f:
        syntax_data = json.load(f)

    semantics = load_existing_semantics()

    # Extract all parameter names from syntax
    syntax_params = set()
    for structure_name, structure in syntax_data.items():
        if 'parameters' in structure:
            for param in structure['parameters']:
                if isinstance(param, dict) and param.get('condition') == 'parameter':
                    param_name = param.get('name', '').split('[')[0].strip()
                    if param_name and not param_name.startswith('//'):
                        syntax_params.add(param_name)

    missing = syntax_params - set(semantics.keys())
    return sorted(missing)

def extract_text_from_docx(doc_path, start_section=7.3, end_section=7.5):
    """Extract text from sections 7.3-7.4 (semantics sections)"""
    doc = Document(doc_path)
    text_chunks = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            text_chunks.append(text)

    # Join and return
    full_text = '\n'.join(text_chunks)

    # Find section 7.3 onwards (semantics start here)
    try:
        section_7_3_idx = full_text.find('7.3')
        if section_7_3_idx != -1:
            return full_text[section_7_3_idx:section_7_3_idx + 500000]  # Take 500KB of text
    except:
        pass

    return full_text[:500000]  # Fallback: first 500KB

def extract_semantics_with_claude(param_name, spec_text, api_key):
    """Use Claude to extract semantics for a parameter"""
    client = anthropic.Anthropic(api_key=api_key)

    # Reduce spec text to 30KB (~7,500 tokens) to stay within rate limits
    # This allows ~4 requests per minute with the 30K tokens/min limit
    prompt = f"""You are analyzing the H.266/VVC video codec specification document.

I need you to find the semantic definition for this parameter: {param_name}

Here is an excerpt from the specification document (sections 7.3-7.4 which contain semantics):

{spec_text[:30000]}

Please find the semantic definition for "{param_name}" and return it in this EXACT JSON format:
{{
    "parameter": "{param_name}",
    "section": "section number where found (e.g., 7.4.3.2)",
    "definition": "the complete semantic definition text from the spec",
    "constraints": [],
    "related_parameters": []
}}

Rules:
1. The definition should be the EXACT text from the specification
2. Include the complete definition, not just the first sentence
3. If you cannot find it, return: {{"found": false}}
4. Return ONLY the JSON, no other text

Search carefully - the parameter might be defined with variations like:
- "{param_name} specifies..."
- "{param_name} shall..."
- "{param_name} is equal to..."
- "{param_name}, when present, indicates..."
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = message.content[0].text.strip()

        # Try to parse JSON
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()

        result = json.loads(response_text)
        return result

    except Exception as e:
        print(f"Error with Claude API: {e}")
        return {"found": False}

def main():
    print("=" * 80)
    print("Extracting Missing Semantics with Claude AI")
    print("=" * 80)

    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Load document
    print(f"\nLoading specification: {SPEC_PATH}")
    print("Extracting text from specification...")
    spec_text = extract_text_from_docx(SPEC_PATH)
    print(f"✓ Extracted {len(spec_text)} characters")

    # Get missing parameters
    print("\nAnalyzing missing parameters...")
    missing_params = get_missing_parameters()
    print(f"✓ Found {len(missing_params)} missing parameters")

    # Load existing semantics
    semantics = load_existing_semantics()
    added_count = 0
    not_found_count = 0

    print("\nExtracting semantics with Claude AI...")
    print("This will take a while - processing 10 parameters at a time\n")

    for i, param in enumerate(missing_params[:10], 1):  # Start with first 10 to test
        print(f"[{i}/10] {param}...", end=' ', flush=True)

        result = extract_semantics_with_claude(param, spec_text, api_key)

        if result.get('found') == False or 'definition' not in result:
            not_found_count += 1
            print("✗ Not found")
        else:
            semantics[param] = {
                "parameter": result.get('parameter', param),
                "section": result.get('section', ''),
                "definition": result.get('definition', ''),
                "constraints": result.get('constraints', []),
                "related_parameters": result.get('related_parameters', [])
            }
            added_count += 1
            print("✓")

        # Add delay to avoid rate limiting (30K tokens/min limit)
        # With 30KB per request (~7.5K tokens), wait 20 seconds between requests
        if i < len(missing_params[:10]):  # Don't wait after last one
            time.sleep(20)

    print("\n" + "=" * 80)
    print(f"Results:")
    print(f"  Added: {added_count}")
    print(f"  Not found: {not_found_count}")
    print(f"  Total semantics: {len(semantics)}")
    print("=" * 80)

    # Save updated semantics
    print(f"\nSaving to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(semantics, f, indent=2)

    # Also update web version
    web_output = "web/data/vvc/semantics.json"
    print(f"Saving to {web_output}...")
    with open(web_output, 'w') as f:
        json.dump(semantics, f, indent=2)

    print("\n✓ Done!")

if __name__ == "__main__":
    main()
