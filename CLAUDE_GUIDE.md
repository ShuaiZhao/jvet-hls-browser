# Claude Assistant Guide - Interactive HLS Specification Browser

> **For AI Assistants**: This guide helps you quickly understand the project and assist the user effectively.

---

## Quick Start for New Sessions

### 1. Starting the Server

**Primary command:**
```bash
cd "/Users/shzhao/Library/CloudStorage/GoogleDrive-dr.shuai.zhao@gmail.com/My Drive/JVET/HLS/interactive-hls"
python3 server/combined_server.py
```

**Alternative startup scripts:**
```bash
./RUN_SERVER.sh  # macOS/Linux with menu
./RUN_SERVER.bat # Windows with menu
```

**Server details:**
- **Port**: 8000
- **URL**: http://localhost:8000
- **Purpose**: Serves static web files + proxies Claude AI API calls
- **Location**: `server/combined_server.py`

**Login credentials:**
- Username: `admin`
- Password: `admin_password`

### 2. Checking Server Status

```bash
# Check if server is running
lsof -i :8000

# Check for running Python processes
ps aux | grep combined_server.py

# Test server response
curl http://localhost:8000/
```

---

## Project Overview

### What This Project Does

The **Interactive HLS Specification Browser** is a web application that transforms dense video codec specification documents (H.266/VVC, H.265/HEVC, H.264/AVC) into an interactive, clickable website.

**Key Features:**
1. Browse syntax structures from specifications
2. View parameter semantics (definitions, constraints)
3. Explore parameter connections (dependencies, references)
4. AI-powered explanations using Claude API
5. Hierarchical tree visualization of parameter relationships

**User workflow:**
1. User opens http://localhost:8000
2. Logs in with admin/admin_password
3. Clicks syntax structure in left sidebar
4. Clicks parameter to see details in modal
5. Views connections tree showing upstream/downstream relationships
6. Optionally clicks AI robot icon for Claude explanation

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│  OFFLINE PROCESSING (One-Time, already done)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  H.266 Spec DOCX → Parser → syntax.json + semantics.json   │
│                           ↓                                  │
│               Claude Analysis → connections.json             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  RUNTIME (What happens when user browses)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User → Browser → localhost:8000 → combined_server.py       │
│            ↓                              ↓                  │
│       Load JSON files            Proxy AI requests          │
│       (syntax, semantics,        to Claude API              │
│        connections)                                          │
│            ↓                                                 │
│       Display in UI                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.9+ with Flask
- Anthropic Claude API (Sonnet 4.5)
- Combined server on port 8000

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5/CSS3 (responsive)
- Pure CSS tree visualization (no external libraries)
- Font Awesome icons

**Data:**
- Static JSON files (syntax, semantics, connections)
- LocalStorage for AI analysis caching

---

## Directory Structure

```
interactive-hls/
│
├── server/
│   └── combined_server.py          ← START HERE (main server)
│
├── web/                             ← Web application root
│   ├── index.html                   ← Main page
│   ├── login.html                   ← Login page
│   ├── config.json                  ← API key configuration
│   │
│   ├── js/
│   │   ├── app.js                   ← Core logic (1200+ lines)
│   │   ├── connection-graph.js      ← Connection data loading
│   │   └── connection-tree.js       ← Alternative visualization
│   │
│   ├── css/
│   │   └── style.css                ← All styling (~1700 lines)
│   │
│   └── data/
│       └── vvc/
│           ├── syntax.json          ← Syntax structures (306 KB)
│           ├── semantics.json       ← Parameter definitions (721 KB)
│           └── connections.json     ← Parameter relationships (1.2 MB)
│
├── scripts/                         ← Processing scripts (rarely used)
│   ├── process_spec.py              ← Extract syntax/semantics
│   ├── generate_connections_simple.py ← Generate connections with Claude
│   └── verify_semantics_mapping.py  ← Data validation
│
├── parsers/                         ← Spec parsers (rarely modified)
│   └── vvc/
│       └── vvc_parser_v3.py         ← Latest VVC parser
│
├── config/
│   └── codec_config.yaml            ← Codec configuration
│
├── RUN_SERVER.sh                    ← Easy startup script
├── RUN_SERVER.bat                   ← Windows startup script
│
├── README.md                        ← Comprehensive documentation (43 KB)
├── AI_CACHE_FIX.md                  ← AI caching technical docs
└── CONNECTION_TREE_FEATURE.md       ← Tree feature technical docs
```

---

## Key Files Explained

### Server Files

#### `server/combined_server.py` (MOST IMPORTANT)
**Purpose**: Single server handling everything
- Serves static files from `web/` directory
- Proxies `/api/claude` requests to Anthropic
- Port 8000
- No CORS issues
- 60-second timeout for AI requests

**Key functions:**
- `claude_proxy()` - Handles AI API requests
- `serve_static()` - Serves web files
- `serve_index()` - Serves index.html

**Configuration:**
- Reads `ANTHROPIC_API_KEY` from environment or `web/config.json`
- Debug mode: OFF (stable)
- Threaded: ON (concurrent requests)

### Frontend Files

#### `web/js/app.js` (CORE LOGIC)
**Size**: ~1200 lines
**Purpose**: All application logic

**Key global variables:**
```javascript
let syntaxData = {};              // All syntax structures
let semanticsData = {};           // All parameter definitions
let connectionsData = {};         // All parameter connections
let currentParameter = null;      // Currently selected parameter
let currentStructure = null;      // Currently selected syntax structure
let currentSemanticsContext = null; // Current context for AI caching
let semanticsHistory = [];        // Navigation history
```

**Key functions:**
- `loadData(codec)` - Load all JSON files
- `displaySyntaxStructure(structure)` - Show syntax in main panel
- `displaySemantics(paramName, pushHistory, syntaxContext)` - Show parameter modal
- `addConnectionsToModal(paramName)` - Add connection tree
- `buildConnectionTree()` - Build tree HTML
- `navigateToParameter(paramName)` - Navigate between parameters
- `aiExplainParameter()` - Get AI explanation with caching

**Important behavior:**
- AI analysis is cleared when switching parameters
- Cache keys include syntax context: `ai_analysis_{codec}_{syntaxContext}_{paramName}`
- Back button uses `semanticsHistory` array

#### `web/css/style.css` (STYLING)
**Size**: ~1700 lines
**Purpose**: All styling including connection tree

**Key sections:**
- Lines 1-500: General layout and components
- Lines 1479-1707: Connection tree styles
  - `.connection-tree-container` - Tree container
  - `.upstream-node` - Blue dependency nodes
  - `.root-node` - Purple current parameter
  - `.downstream-node` - Green reference nodes
  - `.related-node` - Orange related concepts
  - `.tree-connector` - Visual connectors

### Data Files

#### `web/data/vvc/syntax.json` (306 KB)
**Structure:**
```json
{
  "seq_parameter_set_rbsp": {
    "id": "seq_parameter_set_rbsp",
    "section": "7.3.2.1",
    "name": "seq_parameter_set_rbsp",
    "parameters": [
      {
        "name": "sps_seq_parameter_set_id",
        "type": "ue(v)",
        "condition": "parameter"
      }
    ]
  }
}
```

#### `web/data/vvc/semantics.json` (721 KB)
**Structure:**
```json
{
  "sps_seq_parameter_set_id": {
    "parameter": "sps_seq_parameter_set_id",
    "section": "7.4.3.2.1",
    "definition": "identifies the SPS for reference...",
    "constraints": {
      "range": "0..15"
    },
    "related_parameters": ["sps_video_parameter_set_id"]
  }
}
```

#### `web/data/vvc/connections.json` (1.2 MB)
**Structure:**
```json
{
  "sps_seq_parameter_set_id": {
    "dependencies": [
      {
        "parameter": "sps_video_parameter_set_id",
        "context": "SPS depends on VPS",
        "strength": 0.85
      }
    ],
    "references": [
      {
        "parameter": "pps_seq_parameter_set_id",
        "context": "PPS references this SPS",
        "strength": 0.98
      }
    ],
    "related_concepts": [
      {
        "parameter": "alf_adaptation_parameter_set_id",
        "context": "Similar ID pattern",
        "strength": 0.62
      }
    ]
  }
}
```

---

## Recent Major Changes

### 1. Connection Tree Feature (March 2026)

**What changed:**
- Replaced complex D3.js force-directed graph with simple hierarchical tree
- Tree shows only immediate upstream/downstream connections
- All nodes (except root) are clickable for navigation
- Pure CSS implementation, no external libraries

**Files modified:**
- `web/js/app.js` - New tree building logic
- `web/css/style.css` - Added 230+ lines of tree styling

**Key functions:**
- `buildConnectionTree()` - Generates tree HTML (lines 795-882)
- `navigateToParameter()` - Handles node clicks (lines 887-891)

**Tree structure:**
```
[Upstream Dependencies] (Blue)
         ↓
[Current Parameter] (Purple)
         ↓
[Downstream References] (Green)

[Related Concepts] (Orange - separate)
```

### 2. AI Context Isolation Fix (March 2026)

**Problem:** AI analysis was being shared between different syntax structures

**Solution:**
1. Clear AI container when switching parameters
2. Include syntax context in cache keys
3. Add visual context indicator

**Files modified:**
- `web/js/app.js` - Added context tracking and cache clearing

**Key changes:**
- `displaySemantics()` now clears old AI analysis (lines 472-479)
- Cache key format: `ai_analysis_{codec}_{syntaxContext}_{paramName}`
- Added `currentSemanticsContext` global variable

### 3. Combined Server (March 2026)

**What changed:**
- Created single server on port 8000
- Replaced separate static server (8000) + proxy (8001)
- Better error handling and stability

**File created:**
- `server/combined_server.py`

**Benefits:**
- No CORS issues
- Simpler deployment
- Auto-restart capability
- Production-ready configuration

---

## Common User Tasks & How to Help

### Task: "The server stopped"

**Check if running:**
```bash
lsof -i :8000
```

**Start server:**
```bash
cd "/Users/shzhao/Library/CloudStorage/GoogleDrive-dr.shuai.zhao@gmail.com/My Drive/JVET/HLS/interactive-hls"
python3 server/combined_server.py
```

**Debug:**
- Check if port 8000 is blocked
- Check if API key is set
- Look for Python errors in terminal

### Task: "AI analysis is showing wrong context"

**Solution:**
1. Have user clear AI cache in browser console:
```javascript
Object.keys(localStorage)
  .filter(k => k.startsWith('ai_analysis_'))
  .forEach(k => localStorage.removeItem(k));
location.reload();
```

2. Hard refresh browser: Cmd+Shift+R

**Explanation:**
- Each syntax structure should have independent AI cache
- Cache keys include context: `ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id`
- Old AI analysis is cleared when switching parameters

### Task: "Add a new feature to the connection tree"

**Key files to modify:**
1. `web/js/app.js` - Add logic to `buildConnectionTree()` function
2. `web/css/style.css` - Add styling in connection tree section (lines 1479+)

**Example: Add connection strength indicator:**
```javascript
// In buildConnectionTree() function
html += `
  <div class="tree-node upstream-node clickable"
       onclick="navigateToParameter('${conn.name}')">
    <span class="node-name">${conn.name}</span>
    <span class="strength-indicator">${(conn.strength * 100).toFixed(0)}%</span>
  </div>
`;
```

### Task: "Process a new codec"

**Rarely needed, but here's how:**

1. Add codec config to `config/codec_config.yaml`
2. Run processing scripts:
```bash
python scripts/process_spec.py --codec new_codec --skip-ai
python scripts/generate_connections_simple.py new_codec
```

3. Data will be created in `web/data/new_codec/`

---

## Important Context & History

### Why This Architecture?

**Two-phase approach:**
1. **Offline processing** (one-time, ~$3-5): Extract + analyze with Claude
2. **Runtime browsing** (free, instant): Load JSON files, no API calls

**Benefits:**
- Free for end users
- Instant browsing experience
- Deployable to GitHub Pages (static)
- No backend needed after processing

### Why Not Use a Framework?

**Vanilla JS chosen for:**
- Faster initial load
- Smaller bundle size
- No build process
- Deploy anywhere
- Full DOM control

**Trade-offs:**
- More verbose code
- Manual state management
- But simpler for this use case

### Data Generation Timeline

**VVC dataset (already complete):**
- 50+ syntax structures
- 423 parameters with semantics
- ~4,000+ connections
- Generated once in ~60 minutes
- Cost: ~$3-5 USD

**Current status:**
- VVC: Complete ✓
- HEVC: Structure ready, needs processing
- AVC: Structure ready, needs processing

---

## Debugging & Troubleshooting

### Server Won't Start

**Check API key:**
```bash
echo $ANTHROPIC_API_KEY
# or check web/config.json
```

**Check port availability:**
```bash
lsof -i :8000
# If occupied, kill process
kill -9 <PID>
```

**Check Python version:**
```bash
python3 --version  # Should be 3.9+
```

### Frontend Issues

**Check browser console (F12):**
- Look for JavaScript errors
- Check if JSON files loaded
- Verify API calls to /api/claude

**Clear browser cache:**
- Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

**Check data files exist:**
```bash
ls -lh web/data/vvc/
# Should see: syntax.json, semantics.json, connections.json
```

### Connection Tree Not Showing

**Check these:**
1. `connections.json` exists and is valid JSON
2. Browser console for errors
3. CSS loaded correctly (check Network tab)
4. `buildConnectionTree()` function exists in app.js

**Debug in console:**
```javascript
// Check if connections data loaded
console.log(connectionsData);

// Check specific parameter
console.log(connectionsData['sps_seq_parameter_set_id']);
```

---

## Quick Reference Commands

### Server Management

```bash
# Start server (recommended)
cd "/Users/shzhao/Library/CloudStorage/GoogleDrive-dr.shuai.zhao@gmail.com/My Drive/JVET/HLS/interactive-hls"
python3 server/combined_server.py

# Start with script
./RUN_SERVER.sh

# Check if running
lsof -i :8000
curl http://localhost:8000/

# Stop server
# Press Ctrl+C in terminal, or:
pkill -f combined_server.py
```

### Data Validation

```bash
# Validate JSON files
python3 -m json.tool web/data/vvc/syntax.json > /dev/null && echo "✓ syntax.json"
python3 -m json.tool web/data/vvc/semantics.json > /dev/null && echo "✓ semantics.json"
python3 -m json.tool web/data/vvc/connections.json > /dev/null && echo "✓ connections.json"
```

### Git Operations

```bash
# Check status
git status

# Commit changes
git add -A
git commit -m "Description"
git push origin main

# View recent commits
git log --oneline -5
```

---

## Critical Information

### User's Working Directory

```
/Users/shzhao/Library/CloudStorage/GoogleDrive-dr.shuai.zhao@gmail.com/My Drive/JVET/HLS/interactive-hls
```

**Always use this path for:**
- Starting server
- Running scripts
- Git operations

### API Key Location

**Environment variable:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Or config file:**
```
web/config.json
```

### GitHub Repository

```
https://github.com/ShuaiZhao/jvet-hls-browser.git
```

### Important URLs

- **Live Demo**: https://shuaizhao.github.io/jvet-hls-browser/web/
- **Local Dev**: http://localhost:8000
- **Claude Console**: https://console.anthropic.com/

---

## What to Do First in a New Session

1. **Check server status:**
   ```bash
   lsof -i :8000
   ```

2. **If not running, start server:**
   ```bash
   cd "/Users/shzhao/Library/CloudStorage/GoogleDrive-dr.shuai.zhao@gmail.com/My Drive/JVET/HLS/interactive-hls"
   python3 server/combined_server.py
   ```

3. **Read user's request carefully** - understand what they need

4. **Use appropriate tools:**
   - Server issues → Check/start server
   - Frontend bugs → Check app.js, style.css
   - Data issues → Check JSON files
   - New features → Modify app.js + style.css
   - Documentation → Update README.md

5. **Always test changes** if modifying code

6. **Commit and push** when done:
   ```bash
   git add -A
   git commit -m "Description"
   git push origin main
   ```

---

## Documentation Hierarchy

1. **CLAUDE_GUIDE.md** (this file) - Quick reference for AI assistants
2. **README.md** (43 KB) - Comprehensive user guide
3. **AI_CACHE_FIX.md** (8.7 KB) - Technical: AI caching implementation
4. **CONNECTION_TREE_FEATURE.md** (7.8 KB) - Technical: Tree feature details

**For most questions**: README.md has the answer
**For technical details**: Check the specific technical docs
**For quick actions**: Use this guide

---

## Final Notes

**This project is:**
- A web-based specification browser
- For video codec standards (VVC, HEVC, AVC)
- Used by researchers and engineers
- Deployed on GitHub Pages
- Developed with Claude's assistance

**User's typical workflow:**
1. Start server
2. Browse specifications
3. Request new features or fixes
4. Test changes
5. Commit and push

**Your role:**
- Understand the system quickly
- Help implement features
- Debug issues
- Document changes
- Keep code quality high

**Remember:**
- Always start server at the correct path
- Test changes before committing
- Update documentation when needed
- Ask clarifying questions if unsure

---

**Last Updated**: March 2026
**Maintained By**: Claude Code + User
**Project Status**: Active Development

*This guide is specifically for AI assistants to quickly understand and work with this project.*
