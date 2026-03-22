# Interactive HLS Specification Browser

> An AI-powered, interactive web interface for exploring video codec specifications (H.266/VVC, H.265/HEVC, H.264/AVC)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet%204.5-purple.svg)](https://www.anthropic.com/claude)
[![D3.js](https://img.shields.io/badge/D3.js-v7-orange.svg)](https://d3js.org/)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)

---

## Overview

The **Interactive HLS Specification Browser** transforms dense, academic video codec specification documents into an **interactive, clickable website** that makes learning and understanding codec standards effortless.

### What It Does

- **Browse** 50+ syntax structures from H.266/VVC specifications
- **Explore** 423+ parameters with detailed semantic definitions
- **Discover** AI-powered relationships between parameters
- **Visualize** connection graphs with interactive D3.js diagrams
- **Search** and filter across all syntax structures
- **Deploy** as a static website (GitHub Pages compatible)

### Who It's For

- **Students** learning video codec specifications
- **Researchers** in the JVET (Joint Video Experts Team)
- **Engineers** implementing codec software
- **Anyone** curious about modern video compression standards

### Key Benefits

- **One-time AI processing** (~$2-5), unlimited free browsing
- **No backend required** for browsing (pure static files)
- **Instant access** to parameter relationships
- **Visual learning** with interactive connection graphs

---

## Live Demo

Visit: **[https://shuaizhao.github.io/jvet-hls-browser/web/](https://shuaizhao.github.io/jvet-hls-browser/web/)**

**Login Credentials:**
- Username: `admin`
- Password: `admin_password`

---

## Features

### Interactive Syntax Navigation
- Browse 50+ syntax structures from the specification
- Search and filter structures by name
- Click-to-navigate with breadcrumb history

### Comprehensive Semantics
- 423 parameters with AI-extracted definitions
- Constraint information (ranges, valid values)
- Specification section references

### AI-Powered Connections
- Automatic discovery of parameter relationships
- Three connection types:
  - **References**: Direct mentions and references
  - **Dependencies**: Conditional relationships
  - **Related Concepts**: Similar naming/purpose

### Connection Graph Visualization
- Interactive D3.js force-directed graphs
- Color-coded nodes and edges
- Drag, zoom, and click to explore
- Visual connection strength indicators

### Multi-Codec Support
- H.266/VVC (complete)
- H.265/HEVC (structure ready)
- H.264/AVC (structure ready)

### Responsive Design
- Works on desktop, tablet, and mobile
- Resizable panels with drag handles
- Modal dialogs for detailed views

---

## Quick Start

Get running in **5 minutes**:

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/interactive-hls.git
cd interactive-hls
pip install -r requirements.txt
```

### 2. Set Claude API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Get your API key at: https://console.anthropic.com/

### 3. Process VVC Specification

```bash
# Extract syntax and semantics (2-3 minutes, FREE)
python scripts/process_spec.py --codec vvc --skip-ai
```

Output:
- `data/vvc/syntax.json` - All syntax structures
- `data/vvc/semantics.json` - All parameter definitions

### 4. Generate AI Connections

```bash
# Analyze relationships with Claude (30-60 minutes, ~$2-5)
python scripts/generate_connections_simple.py vvc
```

Output:
- `data/vvc/connections.json` - All parameter relationships

### 5. Open Web Interface

```bash
cd web
python -m http.server 8000
```

Open browser to: **http://localhost:8000**

Done! Browse your interactive specification.

---

## Table of Contents

- [Installation](#installation)
- [Processing Specifications](#processing-specifications)
- [Usage Guide](#usage-guide)
- [How It Works](#how-it-works)
- [Deployment](#deployment)
- [Advanced Topics](#advanced-topics)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Statistics](#statistics)
- [Contributing](#contributing)
- [License & Credits](#license--credits)

---

## Installation

### Prerequisites

| Requirement | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.9+ | Backend processing |
| **Claude API Key** | Latest | AI analysis |
| **VVC Specification** | H.266 v3+ | Source document (DOCX) |
| **Web Browser** | Modern | Viewing interface |

### Detailed Setup

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/interactive-hls.git
cd interactive-hls
```

#### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Key Dependencies:**
- `python-docx` - Parse DOCX specification files
- `anthropic` - Claude API integration
- `flask` - Optional API server for real-time analysis
- `pyyaml` - Configuration file parsing

#### 3. Configure Claude API Key

**Option A: Environment Variable**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

**Option B: Configuration File**
Create `web/config.json`:
```json
{
  "anthropic_api_key": "sk-ant-api03-..."
}
```

#### 4. Verify Specification Path

Edit `config/codec_config.yaml` to ensure the path is correct:

```yaml
vvc:
  name: "VVC/H.266"
  spec_file: "../H266_VVC/H266-VVC-v3.docx"
```

Update the path to match your local specification file location.

---

## Processing Specifications

### Understanding the Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              OFFLINE PROCESSING (One-Time)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  H.266 DOCX Specification                                   │
│         ↓                                                    │
│  [Step 1: Parse Spec]  → syntax.json + semantics.json      │
│         (2-3 minutes, FREE)                                 │
│         ↓                                                    │
│  [Step 2: AI Analysis] → connections.json                   │
│         (30-60 minutes, ~$2-5)                              │
│         ↓                                                    │
│  Static JSON Files (ready for deployment)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               USER BROWSING (Instant, Free)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User opens web/index.html                                  │
│         ↓                                                    │
│  Load JSON files (instant)                                  │
│         ↓                                                    │
│  Browse syntax + semantics + connections                    │
│         (all pre-computed, no API calls!)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Extract Syntax & Semantics

**Fast and free** - no AI calls required:

```bash
python scripts/process_spec.py --codec vvc --skip-ai
```

**What it does:**
1. Opens the DOCX specification file
2. Finds Section 7.3 (Syntax) and Section 7.4 (Semantics)
3. Extracts syntax structures from tables
4. Parses parameter definitions and constraints
5. Creates JSON files for web interface

**Output:**
```
✓ data/vvc/syntax.json       (306 KB, 50+ structures)
✓ data/vvc/semantics.json    (721 KB, 423 definitions)
```

**Time:** 2-3 minutes
**Cost:** FREE (no API calls)

### Step 2: Generate AI Connections

**Uses Claude to analyze parameter relationships:**

```bash
python scripts/generate_connections_simple.py vvc
```

**What it does:**
1. Loads all parameter definitions from semantics.json
2. For each parameter, prompts Claude to identify:
   - **References**: Parameters mentioned in the definition
   - **Dependencies**: Conditional relationships
   - **Related Concepts**: Similar parameters
3. Assigns connection strength scores (0-1)
4. Saves to connections.json

**Progress output:**
```
==========================================================
Generating connections for VVC using Claude
==========================================================

Loading data...
✓ Loaded 423 parameters

Analyzing parameters...
[1/423] sps_seq_parameter_set_id... ✓ 8 connections
[2/423] sps_video_parameter_set_id... ✓ 5 connections
[3/423] sps_chroma_format_idc... ✓ 12 connections
...
[423/423] Complete!

Saved to: data/vvc/connections.json
```

**Time:** 30-60 minutes (3-second delays between API calls)
**Cost:** ~$2-5 USD (Sonnet 4.5 at ~$0.01/parameter)

**Cost breakdown:**
- Input tokens: ~500-1000 per parameter
- Output tokens: ~200-500 per parameter
- Total per parameter: ~$0.008-0.015
- For 423 parameters: ~$3.40-6.35

### Processing Other Codecs

#### HEVC/H.265

```bash
# 1. Extract syntax and semantics
python scripts/process_spec.py --codec hevc --skip-ai

# 2. Generate connections
python scripts/generate_connections_simple.py hevc
```

#### AVC/H.264

```bash
# 1. Extract syntax and semantics
python scripts/process_spec.py --codec avc --skip-ai

# 2. Generate connections
python scripts/generate_connections_simple.py avc
```

**Note:** Make sure the specification paths in `config/codec_config.yaml` are correct.

---

## Usage Guide

### Opening the Web Interface

**Option 1: Direct File Access**
```bash
# Just open in browser
open web/index.html  # macOS
xdg-open web/index.html  # Linux
start web/index.html  # Windows
```

**Option 2: Local Web Server (Recommended)**
```bash
cd web
python -m http.server 8000
```

Open: **http://localhost:8000**

### Browsing Syntax Structures

1. **Left Sidebar**: Shows all syntax structures
   - Example: `seq_parameter_set_rbsp`, `slice_header`, `pic_parameter_set_rbsp`
   - Section badges show specification references (e.g., "7.3.2.1")

2. **Search Box**: Filter structures by name
   - Type "sps" to find all SPS-related structures
   - Real-time filtering as you type

3. **Click Structure**: Main panel displays the syntax
   - C++-style code formatting
   - Clickable parameter names (blue links)
   - Function calls preserved (e.g., `slice_header()`)
   - Control flow shown (if/while statements)

### Viewing Parameter Details

1. **Click any parameter name** (e.g., `sps_chroma_format_idc`)

2. **Semantics Tab** displays:
   - **Parameter Name**: Full identifier
   - **Section Reference**: Where it's defined in the spec
   - **Definition**: Complete semantic description
   - **Constraints**:
     - Value ranges (e.g., "0..15")
     - Valid values and meanings
   - **Related Parameters**: Cross-references

3. **Connections Tab** shows:
   - **Inline Connection Graph**: Interactive D3.js visualization
   - **Color-coded nodes**:
     - Pink: Root (selected parameter)
     - Purple: Level 1 connections
     - Blue: Level 2 connections
   - **Edge types**: References, Dependencies, Related

4. **AI Explain Tab** (optional):
   - Click robot icon for AI-powered explanation
   - Context-aware analysis
   - Cached per syntax structure
   - Visual indicators: cache status, timestamp

### Understanding the Connection Graph

**Node Colors:**
- **Pink**: Root node (the parameter you clicked)
- **Purple**: Direct connections (level 1)
- **Blue**: Secondary connections (level 2)

**Edge Types:**
- **Solid**: Strong relationship
- **Dashed**: Weak relationship

**Interactions:**
- **Drag nodes**: Rearrange the graph
- **Click node**: Navigate to that parameter
- **Zoom**: Mouse wheel or pinch gesture
- **Pan**: Click and drag background

**Connection Types:**
- **References**: Parameter A references Parameter B in its definition
  - Example: `pps_seq_parameter_set_id` references `sps_seq_parameter_set_id`
- **Dependencies**: Parameter A depends on Parameter B's value
  - Example: `separate_colour_plane_flag` depends on `sps_chroma_format_idc == 3`
- **Related Concepts**: Parameters with similar naming or purpose
  - Example: `sps_max_width` ~ `sps_max_height`

### Navigation Features

- **Back Button**: Return to previous parameter
- **History Stack**: Navigate through your exploration path
- **Cross-references**: Click any parameter name to jump to its definition
- **Breadcrumbs**: See current syntax structure context

### Switching Codecs

- **Dropdown Menu**: Top-right corner
- Select: VVC, HEVC, or AVC
- Data loads automatically
- Interface adapts to selected codec

---

## How It Works

### Architecture Overview

The system operates in **two distinct phases**:

#### Phase 1: Offline Processing (One-Time)

```
DOCX Specification
    ↓
[VVC Parser]
    ├─ Extract syntax structures (Section 7.3)
    ├─ Extract parameter semantics (Section 7.4)
    ├─ Parse constraints and value ranges
    └─ Create JSON files
    ↓
syntax.json + semantics.json
    ↓
[Claude AI Analyzer]
    ├─ For each parameter:
    │   ├─ Read definition + context
    │   ├─ Identify references
    │   ├─ Find dependencies
    │   ├─ Discover related concepts
    │   └─ Assign strength scores
    └─ Create connections.json
    ↓
Static JSON Files (ready to deploy!)
```

#### Phase 2: Runtime (User Browsing)

```
User opens web/index.html
    ↓
[JavaScript App]
    ├─ Load syntax.json (all structures)
    ├─ Load semantics.json (all definitions)
    ├─ Load connections.json (all relationships)
    └─ Render UI
    ↓
User clicks parameter
    ↓
[Display Logic]
    ├─ Look up semantics[parameter_name]
    ├─ Look up connections[parameter_name]
    ├─ Render D3.js graph
    └─ Show in modal
    ↓
Everything is instant (no API calls!)
```

### Technology Stack

#### Backend Processing (Python)

| Technology | Purpose | Version |
|-----------|---------|---------|
| **python-docx** | Parse DOCX files | 1.1.0+ |
| **anthropic** | Claude API | 0.18.0+ |
| **flask** | Optional API server | 3.0.0+ |
| **pyyaml** | Config parsing | 6.0.1+ |
| **beautifulsoup4** | HTML/text extraction | 4.12.0+ |

#### Frontend (Web)

| Technology | Purpose | Version |
|-----------|---------|---------|
| **Vanilla JavaScript** | Application logic | ES6+ |
| **D3.js** | Graph visualization | v7 |
| **HTML5/CSS3** | Structure & styling | Latest |
| **Font Awesome** | Icons | 6.4.0 |

#### AI Integration

| Service | Model | Purpose |
|---------|-------|---------|
| **Anthropic Claude** | Sonnet 4.5 | Connection analysis |
| **Temperature** | 0.3 | Consistent analysis |
| **Max Tokens** | 2000 | Detailed responses |

### Data Format Specifications

#### syntax.json

```json
{
  "seq_parameter_set_rbsp": {
    "id": "seq_parameter_set_rbsp",
    "section": "7.3.2.1",
    "name": "seq_parameter_set_rbsp",
    "descriptor": "Sequence parameter set RBSP syntax",
    "parameters": [
      {
        "name": "sps_seq_parameter_set_id",
        "type": "ue(v)",
        "condition": "parameter",
        "semantics_ref": "sps_seq_parameter_set_id"
      },
      {
        "name": "if( sps_video_parameter_set_id == 0 ) {",
        "type": "",
        "condition": "if_statement",
        "semantics_ref": null
      }
    ]
  }
}
```

#### semantics.json

```json
{
  "sps_seq_parameter_set_id": {
    "parameter": "sps_seq_parameter_set_id",
    "section": "7.4.3.2.1",
    "definition": "sps_seq_parameter_set_id identifies the SPS for reference by other syntax elements. The value shall be in the range of 0 to 15, inclusive.",
    "constraints": {
      "range": "0..15",
      "values": {}
    },
    "related_parameters": [
      "sps_video_parameter_set_id",
      "pps_seq_parameter_set_id"
    ]
  }
}
```

#### connections.json

```json
{
  "sps_seq_parameter_set_id": {
    "references": [
      {
        "parameter": "pps_seq_parameter_set_id",
        "type": "referenced_by",
        "context": "PPS references this SPS identifier",
        "strength": 0.98
      }
    ],
    "dependencies": [
      {
        "parameter": "sps_video_parameter_set_id",
        "type": "dependency",
        "context": "SPS depends on VPS when VPS ID > 0",
        "strength": 0.85
      }
    ],
    "related_concepts": [
      {
        "parameter": "alf_adaptation_parameter_set_id",
        "type": "related",
        "context": "Similar ID naming pattern for parameter sets",
        "strength": 0.62
      }
    ]
  }
}
```

### Key Design Decisions

#### Why Pre-computed Connections?

**Advantages:**
- ✅ Instant browsing (no API delays)
- ✅ Zero cost for users
- ✅ Works offline after deployment
- ✅ Deployable to GitHub Pages (static)

**Trade-offs:**
- One-time AI cost (~$2-5)
- Connections can't be customized at runtime

#### Why Claude Over Embeddings?

**Claude Analysis (~$2-5):**
- ✅ Understands context and semantics
- ✅ Identifies conditional dependencies
- ✅ Explains relationships
- ✅ Better quality

**Embeddings (~$0.50-1):**
- ❌ Only similarity matching
- ❌ No conditional logic
- ❌ No explanation
- ✅ Cheaper

**Verdict:** Claude provides significantly better quality for a small cost increase.

#### Why No Frontend Framework?

**Vanilla JS Approach:**
- ✅ Faster initial load
- ✅ Smaller bundle size
- ✅ No build process
- ✅ Deploy anywhere (GitHub Pages, etc.)
- ✅ Full control over DOM

**Trade-offs:**
- More verbose code
- Manual state management

---

## Deployment

### Option 1: GitHub Pages (Static, Free)

Perfect for browsing with pre-computed connections.

#### Step 1: Prepare Files

```bash
# Create docs folder for GitHub Pages
mkdir -p docs

# Copy web files
cp -r web/* docs/

# Copy data files
cp -r data docs/
```

#### Step 2: Configure Repository

1. Go to GitHub repository → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / **docs**
4. Click **Save**

#### Step 3: Access Your Site

Your site will be available at:
```
https://yourusername.github.io/repository-name/
```

**Example:** https://shuaizhao.github.io/jvet-hls-browser/web/

#### Step 4: Update Login Credentials

Edit `docs/login.html` to change default credentials:

```javascript
// Change these values
const validCredentials = {
  username: 'your_username',
  password: 'your_password'
};
```

### Option 2: Netlify (Static, Free)

#### Via Git

1. Push your repository to GitHub
2. Go to https://netlify.com
3. Click **"New site from Git"**
4. Select your repository
5. **Build settings:**
   - Base directory: `web`
   - Publish directory: `web`
6. Click **"Deploy site"**

#### Via Drag-and-Drop

1. Go to https://app.netlify.com/drop
2. Drag the `web` folder
3. Done!

### Option 3: Vercel (Static, Free)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from web directory
cd web
vercel
```

Follow the prompts to complete deployment.

### Option 4: Custom Server

#### Using Python HTTP Server

```bash
cd web
python -m http.server 80
```

Access at: http://your-server-ip/

#### Using Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /path/to/interactive-hls/web;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Optional: Real-Time AI Analysis Server

For **on-demand AI explanations** (optional feature):

#### Deploy Flask API

**Option A: Railway (Free tier)**

1. Create `Procfile`:
```
web: cd web/backend && python api_server.py
```

2. Deploy:
```bash
railway login
railway init
railway up
```

**Option B: Render (Free tier)**

1. Create account at https://render.com
2. New → **Web Service**
3. Connect repository
4. Settings:
   - Environment: **Python 3**
   - Build command: `pip install -r requirements.txt`
   - Start command: `cd web/backend && python api_server.py`
5. Add environment variable: `ANTHROPIC_API_KEY`

**Option C: Heroku**

```bash
# Create app
heroku create your-app-name

# Set API key
heroku config:set ANTHROPIC_API_KEY="sk-ant-..."

# Deploy
git push heroku main
```

#### Update Frontend Configuration

Edit `web/config.json`:

```json
{
  "api_url": "https://your-api-server.com",
  "anthropic_api_key": ""
}
```

---

## Advanced Topics

### Customizing Connection Analysis

Edit `scripts/generate_connections_simple.py` to change how Claude analyzes parameters:

```python
# Find the prompt template (around line 50-100)
prompt = f"""Analyze the following parameter from the H.266/VVC specification:

Parameter: {param_name}
Definition: {param_def}

Focus on:
1. Control flow dependencies (if/when conditions)
2. Mathematical derivations
3. Value range relationships
4. Naming pattern similarities

[Add your custom instructions here]

Return JSON with:
{{
  "references": [...],
  "dependencies": [...],
  "related_concepts": [...]
}}
"""
```

**Customization ideas:**
- Add weight to certain connection types
- Focus on specific relationship patterns
- Include algorithm pseudocode analysis
- Extract table references

### Extending the Parser

#### Add New Specification Sections

Edit `parsers/vvc/vvc_parser_v3.py`:

```python
def extract_additional_data(self):
    """Extract tables, algorithms, etc."""
    # Find Section 8 (Decoding process)
    section_8 = self._find_section("8")

    # Extract algorithms
    algorithms = self._extract_algorithms(section_8)

    return algorithms
```

Update `scripts/process_spec.py` to call your new extraction method.

#### Support New Codecs

1. Create new parser in `parsers/your_codec/`:

```python
from parsers.base_parser import BaseSpecParser

class YourCodecParser(BaseSpecParser):
    def extract_syntax_structures(self):
        # Implement codec-specific extraction
        pass
```

2. Add configuration in `config/codec_config.yaml`:

```yaml
your_codec:
  name: "Your Codec Name"
  spec_file: "/path/to/spec.docx"
  syntax_section: "X.X"
  semantics_section: "X.X"
  parser_class: "your_codec.YourCodecParser"
```

3. Process:

```bash
python scripts/process_spec.py --codec your_codec
```

### UI Customization

#### Change Color Scheme

Edit `web/css/style.css`:

```css
/* Header gradient */
.header {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

/* Connection graph node colors */
.node-root { fill: #your-root-color; }
.node-level1 { fill: #your-level1-color; }
.node-level2 { fill: #your-level2-color; }
```

#### Modify Layout

Edit `web/index.html` to change the grid structure:

```html
<!-- Change grid template columns -->
<style>
  .main-container {
    grid-template-columns: 250px 1fr 400px; /* sidebar | main | details */
  }
</style>
```

#### Add New Features

Example: Add a "Copy Definition" button

1. Edit `web/js/app.js`:

```javascript
function displaySemantics(paramName, syntaxContext) {
    // ... existing code ...

    // Add copy button
    const copyBtn = document.createElement('button');
    copyBtn.textContent = 'Copy Definition';
    copyBtn.onclick = () => {
        navigator.clipboard.writeText(semantics.definition);
    };

    detailsDiv.appendChild(copyBtn);
}
```

2. Style in `web/css/style.css`:

```css
.copy-btn {
    background: #4CAF50;
    color: white;
    padding: 8px 16px;
    border: none;
    cursor: pointer;
}
```

### Optimizing AI Costs

#### Reduce Number of Parameters

Only analyze frequently-used parameters:

```python
# In generate_connections_simple.py
important_params = ['sps_', 'pps_', 'slice_', 'ph_']
filtered_params = [p for p in all_params if any(p.startswith(prefix) for prefix in important_params)]
```

#### Use Caching

The script already caches results, but you can enhance it:

```python
import json
import os

CACHE_FILE = 'connections_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_to_cache(param, connections):
    cache = load_cache()
    cache[param] = connections
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)
```

#### Batch Processing

Process parameters in batches to reduce API calls:

```python
# Analyze multiple parameters in one prompt
batch_size = 5
for i in range(0, len(params), batch_size):
    batch = params[i:i+batch_size]
    # Combine parameters in single prompt
    # ...
```

---

## Troubleshooting

### Common Issues

#### 1. "ANTHROPIC_API_KEY not set"

**Problem:** API key not configured

**Solutions:**

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# For Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-api03-..."

# Or add to web/config.json
{
  "anthropic_api_key": "sk-ant-api03-..."
}
```

#### 2. "No syntax data available"

**Problem:** JSON files not generated

**Solution:**

```bash
# Run processing script
python scripts/process_spec.py --codec vvc --skip-ai

# Verify files exist
ls -la data/vvc/
# Should see: syntax.json, semantics.json
```

#### 3. "Specification file not found"

**Problem:** DOCX file path incorrect

**Solution:**

Edit `config/codec_config.yaml`:

```yaml
vvc:
  spec_file: "/absolute/path/to/H266-VVC-v3.docx"
```

Verify file exists:
```bash
ls -la ../H266_VVC/H266-VVC-v3.docx
```

#### 4. "Connection data not available"

**Problem:** connections.json not generated

**Solution:**

```bash
# Generate connections
python scripts/generate_connections_simple.py vvc

# This takes 30-60 minutes - be patient!
```

#### 5. Claude API Rate Limiting

**Problem:** "Rate limit exceeded" error

**Solutions:**

1. **Wait**: Rate limits reset after a few minutes

2. **Increase delay** in `generate_connections_simple.py`:
```python
time.sleep(5)  # Change from 3 to 5 seconds
```

3. **Use checkpoint**: The script saves progress, just re-run:
```bash
python scripts/generate_connections_simple.py vvc
# It will resume from checkpoint
```

#### 6. Web Interface Not Loading

**Problem:** Blank page or JavaScript errors

**Solutions:**

1. **Check browser console** (F12 → Console)

2. **Verify file paths**:
```javascript
// In web/js/app.js, check data paths
const dataPath = `data/${codec}/`;
```

3. **Use web server** instead of file:// protocol:
```bash
cd web
python -m http.server 8000
# Open http://localhost:8000
```

4. **Clear browser cache**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

#### 7. Graph Not Rendering

**Problem:** Connection graph shows empty or errors

**Solutions:**

1. **Check D3.js loaded**:
```html
<!-- In web/index.html -->
<script src="https://d3js.org/d3.v7.min.js"></script>
```

2. **Verify connections.json**:
```bash
# Check file exists and is valid JSON
cat data/vvc/connections.json | python -m json.tool
```

3. **Check browser console** for D3.js errors

#### 8. Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'anthropic'`

**Solution:**

```bash
# Reinstall requirements
pip install -r requirements.txt

# Or install specific package
pip install anthropic

# Verify installation
python -c "import anthropic; print('OK')"
```

#### 9. Incorrect Semantics Displayed

**Problem:** Parameter shows wrong definition

**Known Issue:** Some parameters may have mapping errors

**Solution:**

1. **Report issue**: Note the parameter name and incorrect mapping

2. **Manual fix** in `data/vvc/semantics.json`:
```json
{
  "parameter_name": {
    "definition": "Corrected definition here"
  }
}
```

3. **Run verification script**:
```bash
python scripts/verify_semantics_mapping.py
```

### Debug Commands

```bash
# Test API key
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY', 'NOT SET'))"

# Validate JSON files
python -m json.tool data/vvc/syntax.json > /dev/null && echo "syntax.json: OK"
python -m json.tool data/vvc/semantics.json > /dev/null && echo "semantics.json: OK"
python -m json.tool data/vvc/connections.json > /dev/null && echo "connections.json: OK"

# Check Python version
python --version  # Should be 3.9+

# List installed packages
pip list | grep -E "(anthropic|docx|flask)"

# Test web server
curl http://localhost:8000/index.html

# Check port availability
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

### Getting Help

1. **Check documentation**: Review this README and other docs
2. **Search issues**: GitHub Issues for known problems
3. **Enable debug mode**: Add `console.log()` statements in JavaScript
4. **Report bugs**: Open a GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version, browser)
   - Relevant log output

---

## Project Structure

```
interactive-hls/
│
├── web/                          # Frontend application
│   ├── index.html               # Main application entry
│   ├── login.html               # Authentication page
│   ├── config.json              # API configuration
│   │
│   ├── css/
│   │   └── style.css            # All styling (responsive)
│   │
│   ├── js/
│   │   ├── app.js               # Core application logic (1200+ lines)
│   │   ├── connection-graph.js  # D3.js graph visualization
│   │   └── connection-tree.js   # Tree view (legacy)
│   │
│   ├── data/                    # Static data files
│   │   ├── vvc/
│   │   │   ├── syntax.json      # VVC syntax structures (306 KB)
│   │   │   ├── semantics.json   # VVC semantics (721 KB)
│   │   │   └── connections.json # VVC connections (1.2 MB)
│   │   ├── hevc/                # HEVC data (pending)
│   │   └── avc/                 # AVC data (pending)
│   │
│   └── backend/                 # Optional API server
│       └── api_server.py        # Flask server for real-time AI
│
├── scripts/                      # Processing scripts
│   ├── process_spec.py          # Main orchestration (entry point)
│   ├── extract_semantics_with_ai.py    # AI semantics extraction
│   ├── generate_connections_simple.py  # Claude connection analysis
│   ├── generate_connections.py         # Alternative (embeddings)
│   ├── verify_semantics_mapping.py     # QA validation
│   ├── fix_semantics_references.py     # Data correction
│   └── extract_missing_semantics.py    # Recovery tool
│
├── parsers/                      # Specification parsers
│   ├── base_parser.py           # Abstract base class
│   ├── vvc/
│   │   ├── vvc_parser.py        # First version
│   │   ├── vvc_parser_v2.py     # Enhanced version
│   │   └── vvc_parser_v3.py     # Latest (full syntax extraction)
│   ├── hevc/                    # HEVC parser (stub)
│   └── avc/                     # AVC parser (stub)
│
├── config/                       # Configuration files
│   ├── codec_config.yaml        # Codec definitions, paths, patterns
│   └── api_config.yaml          # API settings
│
├── data/                         # Alternative data location
│   └── vvc/                     # Mirrors web/data/vvc/
│
├── server/                       # Legacy proxy server
│   └── proxy.py                 # Flask CORS proxy (port 8001)
│
├── docs/                         # Documentation
│   └── (auto-generated or manual docs)
│
├── requirements.txt              # Python dependencies
├── setup.sh                      # Setup script
├── .gitignore                   # Git ignore patterns
│
├── README.md                    # This file
├── QUICKSTART.md                # 5-minute quick start
├── GETTING_STARTED.md           # Detailed setup guide
└── PROGRESS.md                  # Development status
```

### Key Files Explained

| File | Purpose | Size | Lines |
|------|---------|------|-------|
| `web/index.html` | Main application HTML | 6.4 KB | ~200 |
| `web/js/app.js` | Core application logic | 46 KB | 1200+ |
| `web/js/connection-graph.js` | D3.js graph visualization | 14 KB | ~400 |
| `web/css/style.css` | All styling | Large | ~1500 |
| `parsers/base_parser.py` | Parser base class | 7 KB | 220 |
| `parsers/vvc/vvc_parser_v3.py` | Latest VVC parser | Large | ~500 |
| `scripts/process_spec.py` | Main entry point | 6 KB | 186 |
| `scripts/generate_connections_simple.py` | Claude connection analysis | ~8 KB | 200+ |
| `config/codec_config.yaml` | Codec configuration | 4 KB | 127 |

### Data Files

| File | Description | Format | Size (VVC) |
|------|-------------|--------|------------|
| `syntax.json` | All syntax structures | JSON | 306 KB |
| `semantics.json` | All parameter definitions | JSON | 721 KB |
| `connections.json` | All parameter relationships | JSON | 1.2 MB |

---

## Statistics

### VVC Dataset (H.266)

| Metric | Value |
|--------|-------|
| **Syntax Structures** | 50+ |
| **Total Parameters** | 423 |
| **Parameters with Semantics** | 423 (100%) |
| **Parameters with Connections** | 423 (100%) |
| **Average Connections per Parameter** | 8-12 |
| **Total Connection Relationships** | ~4,000+ |
| **Specification Sections Covered** | 7.3, 7.4 (HLS) |

### Processing Performance

| Task | Time | Cost |
|------|------|------|
| **Syntax Extraction** | 1-2 min | FREE |
| **Semantics Extraction** | 1 min | FREE |
| **Connection Analysis** | 30-60 min | $2-5 |
| **Total Offline Processing** | ~35-65 min | $2-5 |

### Runtime Performance

| Operation | Time | Cost |
|-----------|------|------|
| **Load JSON Files** | <1 sec | FREE |
| **Render Syntax Structure** | <100 ms | FREE |
| **Display Parameter Semantics** | <50 ms | FREE |
| **Render Connection Graph** | <500 ms | FREE |
| **All Browsing** | Instant | FREE |

### File Sizes

| Codec | Syntax | Semantics | Connections | Total |
|-------|--------|-----------|-------------|-------|
| **VVC** | 306 KB | 721 KB | 1.2 MB | ~2.2 MB |
| **HEVC** | TBD | TBD | TBD | TBD |
| **AVC** | TBD | TBD | TBD | TBD |

### AI Usage (VVC)

| Metric | Value |
|--------|-------|
| **Total Parameters Analyzed** | 423 |
| **Claude API Calls** | 423 |
| **Average Input Tokens** | ~750/param |
| **Average Output Tokens** | ~350/param |
| **Total Tokens** | ~465,000 |
| **Estimated Cost** | $3.40-6.35 |
| **Time (with 3s delays)** | ~35-45 min |

---

## Contributing

We welcome contributions from the community!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit**: `git commit -m "Add your feature"`
6. **Push**: `git push origin feature/your-feature`
7. **Open a Pull Request**

### Areas for Contribution

- **Parser improvements**: Better extraction of syntax structures
- **Additional codecs**: HEVC and AVC parsers
- **UI enhancements**: Better visualizations, dark mode
- **Documentation**: Tutorials, examples, translations
- **Bug fixes**: See GitHub Issues for known bugs
- **Performance optimizations**: Faster parsing, rendering
- **New features**: Export, comparison tools, annotations

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: ES6+ features, clear variable names
- **HTML/CSS**: Semantic markup, BEM naming

### Reporting Issues

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Exact steps to trigger the bug
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**:
   - OS (macOS, Windows, Linux)
   - Python version
   - Browser and version
   - Error messages or logs

### Feature Requests

Open a GitHub Issue with:

1. **Use case**: Why this feature is needed
2. **Proposed solution**: How it could work
3. **Alternatives**: Other approaches considered
4. **Additional context**: Screenshots, examples

---

## License & Credits

### License

This project is for **educational and research purposes** only.

The H.266/VVC, H.265/HEVC, and H.264/AVC specifications are owned by:
- **ITU-T** (International Telecommunication Union)
- **ISO/IEC** (International Organization for Standardization)

Please refer to official sources for licensing information regarding the specifications themselves.

### Specification Sources

- **H.266/VVC**: ITU-T H.266 | ISO/IEC 23090-3 (2020+)
- **H.265/HEVC**: ITU-T H.265 | ISO/IEC 23008-2 (2013+)
- **H.264/AVC**: ITU-T H.264 | ISO/IEC 14496-10 (2003+)

### Credits

- **Developed for**: JVET (Joint Video Experts Team)
- **AI Integration**: Anthropic Claude Sonnet 4.5
- **Visualization**: D3.js community
- **Icons**: Font Awesome

### Acknowledgments

Special thanks to:
- The JVET standardization committee
- Anthropic for Claude API
- The open-source community
- Contributors and users of this tool

---

## Support & Contact

### Documentation

- **This README**: Complete setup and usage guide
- **QUICKSTART.md**: 5-minute quick start
- **GETTING_STARTED.md**: Detailed setup guide
- **PROGRESS.md**: Development status and history

### Getting Help

1. **Check documentation**: Review all markdown files
2. **Search issues**: [GitHub Issues](https://github.com/yourusername/interactive-hls/issues)
3. **Ask questions**: Open a new issue with "Question" label
4. **Community**: Discussions tab for general questions

### Reporting Bugs

Open a GitHub Issue with:
- Clear title
- Description
- Steps to reproduce
- Environment details
- Expected vs actual behavior

### Contact

- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Email**: your.email@example.com
- **Project**: https://github.com/yourusername/interactive-hls

---

## Quick Reference

### Essential Commands

```bash
# Setup
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# Process VVC
python scripts/process_spec.py --codec vvc --skip-ai
python scripts/generate_connections_simple.py vvc

# Start web server
cd web && python -m http.server 8000

# Validate data
python -m json.tool data/vvc/syntax.json
python -m json.tool data/vvc/semantics.json
python -m json.tool data/vvc/connections.json
```

### File Locations

- **Data**: `data/vvc/*.json` or `web/data/vvc/*.json`
- **Config**: `config/codec_config.yaml`
- **Parser**: `parsers/vvc/vvc_parser_v3.py`
- **Scripts**: `scripts/process_spec.py`, `scripts/generate_connections_simple.py`
- **Web**: `web/index.html`, `web/js/app.js`

### URLs

- **Live Demo**: https://shuaizhao.github.io/jvet-hls-browser/web/
- **Documentation**: See markdown files in repository
- **Claude API**: https://console.anthropic.com/
- **D3.js Docs**: https://d3js.org/

---

**Made with ❤️ for the video codec community**

*Explore. Learn. Understand.*
