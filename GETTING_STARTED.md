# Getting Started - Interactive HLS Browser

Complete guide to set up and use the Interactive HLS Specification Browser.

## Overview

This tool creates an **interactive, clickable website** for video codec specifications (VVC, HEVC, AVC). Features:

- Click on syntax structures to see parameters
- Click on parameters to see semantics + connections
- AI-powered connection discovery (using Claude)
- Static website (deployable to GitHub Pages)
- No AI cost when browsing (all pre-computed)

## Complete Workflow

### Phase 1: Offline Processing (One-Time)

```
┌─────────────────────┐
│  H266-VVC-v3.docx   │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Step 1:      │
    │ Parse Spec   │  → syntax.json + semantics.json
    └──────┬───────┘    (2-3 minutes, FREE)
           │
           ▼
    ┌──────────────┐
    │ Step 2:      │
    │ Claude       │  → connections.json
    │ Analysis     │    (30-60 min, ~$2-5)
    └──────────────┘
```

### Phase 2: User Browsing (Fast, Free)

```
User opens web/index.html
    ↓
Loads JSON files (instant)
    ↓
User clicks parameter
    ↓
Shows semantics + connections (instant, no AI calls!)
```

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd interactive-hls
pip install -r requirements.txt
```

Requirements:
- `python-docx` - Parse DOCX files
- `anthropic` - Claude API
- `pyyaml` - Configuration files
- Other standard libraries

### 2. Set Claude API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Get a key at: https://console.anthropic.com/

### 3. Process VVC Specification

```bash
# Step 1: Extract syntax and semantics (fast, free)
python scripts/process_spec.py --codec vvc --skip-ai

# Output:
# ✓ data/vvc/syntax.json (all syntax structures)
# ✓ data/vvc/semantics.json (all semantic definitions)
```

### 4. Generate Connections with Claude

```bash
# Step 2: Analyze connections (slower, uses Claude API)
python scripts/generate_connections_simple.py vvc

# This will:
# - Analyze each parameter using Claude
# - Find references, dependencies, related concepts
# - Save to data/vvc/connections.json
#
# Time: ~30-60 minutes for ~200-300 parameters
# Cost: ~$2-5 (depends on # of parameters)
```

**Progress output:**
```
==========================================================
Generating connections for VVC using Claude
==========================================================

Loading data...
✓ Loaded 287 parameters

Analyzing parameters...
(This may take a while for large specs)

[1/287] Analyzing sps_seq_parameter_set_id... ✓ Found 8 connections
[2/287] Analyzing sps_video_parameter_set_id... ✓ Found 5 connections
[3/287] Analyzing sps_chroma_format_idc... ✓ Found 12 connections
...
```

### 5. Open the Web Interface

Simply open `web/index.html` in your browser!

Or use a local server:
```bash
cd web
python -m http.server 8000
# Open http://localhost:8000
```

## Usage Guide

### Browsing Syntax

1. **Left sidebar**: Shows all syntax structures
   - `seq_parameter_set_rbsp`
   - `pic_parameter_set_rbsp`
   - `slice_header`
   - etc.

2. **Click a structure**: Main panel shows syntax table with parameters

3. **Search**: Use search box to filter structures

### Viewing Parameter Details

1. **Click any parameter name** (e.g., `sps_chroma_format_idc`)

2. **Semantics tab** shows:
   - Definition from spec
   - Constraints (ranges, valid values)
   - Related parameters

3. **Connections tab** shows:
   - **References**: Parameters this references
   - **Dependencies**: Conditional dependencies
   - **Related Concepts**: Similar parameters

4. **Click "View Connection Tree"**: See visual graph of connections

### Understanding Connections

**References** (Blue):
- Direct mentions in semantic text
- "sps_seq_parameter_set_id" → "pps_seq_parameter_set_id" (PPS references SPS ID)

**Dependencies** (Pink):
- Conditional presence in syntax
- "separate_colour_plane_flag" depends on "sps_chroma_format_idc == 3"

**Related Concepts** (Gray):
- Similar naming patterns
- Similar semantic meaning
- "sps_max_width" ~ "sps_max_height" (related dimensions)

## Cost Analysis

### OpenAI Approach (Not Recommended)
- Embeddings: ~$0.50-1.00 for 300 parameters
- Total: ~$0.50-1.00
- But: Embeddings don't understand relationships well

### Claude Approach (Recommended)
- Analysis: ~$2-5 for 300 parameters (at ~$0.008-0.015 per analysis)
- Total: ~$2-5
- But: Much better quality, understands context

**One-time cost**, users browse for free!

## Processing Other Codecs

### HEVC/H.265

```bash
# 1. Parse spec
python scripts/process_spec.py --codec hevc --skip-ai

# 2. Generate connections
python scripts/generate_connections_simple.py hevc
```

### AVC/H.264

```bash
# 1. Parse spec
python scripts/process_spec.py --codec avc --skip-ai

# 2. Generate connections
python scripts/generate_connections_simple.py avc
```

Then switch codecs in the web UI dropdown!

## Deployment

### Option 1: GitHub Pages (Static Only)

```bash
# Copy files to docs/ for GitHub Pages
mkdir -p docs
cp -r web/* docs/
cp -r data docs/

# Commit and push
git add .
git commit -m "Add interactive HLS browser"
git push origin main

# Enable GitHub Pages in repo settings → Source: /docs
```

Your site will be at: `https://yourusername.github.io/your-repo`

### Option 2: Any Static Host

Upload these folders to any static host (Netlify, Vercel, Cloudflare Pages):
- `web/` (HTML, CSS, JS)
- `data/` (JSON files)

## File Structure

```
interactive-hls/
├── data/
│   └── vvc/
│       ├── syntax.json          # ← Load instantly
│       ├── semantics.json       # ← Load instantly
│       └── connections.json     # ← Load instantly
├── web/
│   ├── index.html              # ← Open this!
│   ├── css/style.css
│   ├── js/app.js
│   └── backend/                # (optional real-time API)
│       └── api_server.py
├── scripts/
│   ├── process_spec.py         # Parse DOCX
│   └── generate_connections_simple.py  # Claude analysis
└── parsers/
    ├── base_parser.py
    └── vvc/vvc_parser.py
```

## Troubleshooting

### "No syntax data available"
```bash
# Run step 3 first
python scripts/process_spec.py --codec vvc --skip-ai
```

### "No connection data available"
```bash
# Run step 4
python scripts/generate_connections_simple.py vvc
```

### "ANTHROPIC_API_KEY not set"
```bash
# Set the API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### Claude API rate limiting
The script includes 3-second delays between requests to avoid rate limits.

If you hit limits anyway:
- Wait a few minutes
- Adjust `time.sleep(3)` to `time.sleep(5)` in the script

### Parsing errors
Make sure the DOCX file exists at the path in `config/codec_config.yaml`:
```yaml
vvc:
  spec_file: "../H266_VVC/H266-VVC-v3.docx"
```

## Tips for Best Results

1. **Start with VVC**: It has the most complete syntax/semantics structure

2. **Review connections.json**: Claude's analysis is usually very good but may occasionally link unrelated parameters. You can manually edit the JSON if needed.

3. **Adjust Claude prompts**: Edit `generate_connections_simple.py` to customize how Claude analyzes relationships

4. **Customize UI**: Edit `web/css/style.css` to change colors, layout, etc.

5. **Add more metadata**: Extend the parser to extract more information (algorithm pseudocode, tables, etc.)

## Advanced: Customizing Connection Analysis

Edit the prompt in `scripts/generate_connections_simple.py`:

```python
prompt = f"""Analyze this parameter...

Focus on:
1. Control flow dependencies (if/when conditions)
2. Mathematical derivations (equations)
3. Naming patterns (prefixes/suffixes)
4. Semantic similarity (purpose/function)

[Your custom instructions here]
"""
```

## Next Steps

1. ✅ Process VVC specification
2. ✅ Generate connections
3. ✅ Browse locally
4. 📤 Deploy to GitHub Pages
5. 🔄 Process HEVC and AVC
6. 🎨 Customize styling
7. 🚀 Share with others!

## Support

Questions or issues?
1. Check this guide
2. Review QUICKSTART.md
3. Check script output for errors
4. Open a GitHub issue

Enjoy exploring video codec specifications interactively!
