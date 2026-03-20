# Quick Start Guide

Get the Interactive HLS Specification Browser running in 5 minutes!

## Architecture Choice: Real-Time Claude Analysis

This project uses **Claude API for real-time connection analysis** instead of pre-computing embeddings. This approach is:

- **Faster** offline processing (no embedding generation)
- **More accurate** (Claude analyzes with full context on-demand)
- **More cost-effective** (only analyze when users click parameters)
- **Simpler** (no vector database, just JSON files)

## Prerequisites

1. **Python 3.9+**
2. **Anthropic API Key** (for Claude)
   - Get one at: https://console.anthropic.com/
3. **VVC Specification Document** (already in `../H266_VVC/H266-VVC-v3.docx`)

## Step 1: Install Dependencies

```bash
cd interactive-hls
pip install -r requirements.txt
```

## Step 2: Set API Key

```bash
export ANTHROPIC_API_KEY="your-claude-api-key-here"
```

On Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY="your-claude-api-key-here"
```

## Step 3: Process VVC Specification (Fast!)

```bash
python scripts/process_spec.py --codec vvc --skip-ai
```

This extracts syntax and semantics (takes ~2-3 minutes, no AI calls yet).

Output:
```
✓ data/vvc/syntax.json
✓ data/vvc/semantics.json
```

## Step 4: Start the API Server

```bash
cd web/backend
python api_server.py
```

You should see:
```
============================================================
Interactive HLS API Server
============================================================
Claude API configured: True
Starting server on http://localhost:5000
============================================================
```

## Step 5: Open the Web UI

Open `web/index.html` in your browser, or serve it:

```bash
cd web
python -m http.server 8000
```

Then open: **http://localhost:8000**

## How It Works

### Offline Phase (Fast - No AI)

```
VVC DOCX → Parser → JSON Files
          (2-3 min)
```

Creates:
- `syntax.json` - All syntax structures
- `semantics.json` - All semantic definitions

### Real-Time Phase (When User Clicks)

```
User clicks parameter → Flask API → Claude API → Instant analysis
                                    (2-3 sec)
```

Claude analyzes relationships in real-time with full context!

## Usage

1. **Browse Syntax**: Click any syntax structure (e.g., `seq_parameter_set_rbsp`)
2. **Click Parameter**: Click any parameter name (e.g., `sps_chroma_format_idc`)
3. **View Semantics**: See definition, constraints, related parameters
4. **View Connections**: Click "Connections" tab - **Claude analyzes in real-time!**
5. **View Graph**: Click "View Full Connection Tree" to see visual connections

## Cost Estimate

With Claude Sonnet 4.5:
- **Offline processing**: $0 (no AI calls if using `--skip-ai`)
- **Per parameter analysis**: ~$0.01-0.02 (only when user clicks)
- **Per session**: ~$0.50-1.00 (for typical usage of 30-50 parameter clicks)

Much cheaper than pre-computing 1000+ embeddings!

## Troubleshooting

### "Claude API not configured"
```bash
# Make sure API key is set
echo $ANTHROPIC_API_KEY

# If empty, set it:
export ANTHROPIC_API_KEY="your-key"
```

### "No syntax data available"
```bash
# Run the processing script first
python scripts/process_spec.py --codec vvc --skip-ai
```

### API server won't start
```bash
# Install Flask
pip install flask flask-cors

# Check port 5000 is free
lsof -i :5000  # On Mac/Linux
netstat -ano | findstr :5000  # On Windows
```

## Next Steps

1. **Process other codecs**:
   ```bash
   python scripts/process_spec.py --codec hevc --skip-ai
   python scripts/process_spec.py --codec avc --skip-ai
   ```

2. **Deploy to web**:
   - Static files (HTML/CSS/JS) can go to GitHub Pages
   - API server needs a backend (Heroku, Railway, Vercel, etc.)

3. **Customize analysis**:
   - Edit `web/backend/api_server.py` prompts
   - Adjust Claude temperature/max_tokens for different behavior

## Architecture Comparison

### ❌ Old Approach (Slow)
```
Process Spec → Generate 1000+ embeddings → Store in vector DB
               (30-45 minutes, expensive)

User click → Query vector DB → Show pre-computed connections
```

### ✅ New Approach (Fast)
```
Process Spec → Extract syntax/semantics → Store in JSON
               (2-3 minutes, free)

User click → Claude analyzes → Show real-time connections
             (2-3 seconds per click)
```

## FAQ

**Q: Why not use embeddings?**
A: Too slow to generate and Claude is smart enough to analyze without them!

**Q: Can I use OpenAI instead?**
A: Yes! Edit `api_server.py` to use OpenAI's API. Claude is recommended for technical analysis.

**Q: How do I deploy this?**
A: Frontend (HTML/JS) → GitHub Pages (free)
   Backend (Flask API) → Railway/Render/Heroku (free tier available)

**Q: Can it work offline?**
A: Yes for browsing, but connection analysis requires API calls. You could pre-generate connections using the old approach if needed.

## Support

For issues or questions:
1. Check that API key is set correctly
2. Verify JSON files were generated in `data/vvc/`
3. Check API server logs for errors
4. Open a GitHub issue if still stuck!
