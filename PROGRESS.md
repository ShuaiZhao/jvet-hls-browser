# Interactive HLS Specification Browser - Progress Documentation

## Project Overview
An interactive web-based browser for exploring the H.266/VVC (and H.265/H.264) High-Level Syntax specifications with AI-powered semantic analysis and parameter connection visualization.

## Current Status: Active Development

---

## ✅ Completed Features

### 1. Core Infrastructure
- **Web Server**: Python HTTP server serving static files on port 8000
- **API Proxy**: Flask-based proxy server on port 8001 for Claude API calls (bypasses CORS)
- **Authentication**: Session-based login system with configurable credentials
- **Multi-Codec Support**: VVC, HEVC, and AVC codec selection

### 2. Data Extraction & Processing
- **Syntax Extraction**: Automated extraction of syntax structures from specification PDFs
  - Location: `scripts/extract_syntax.py`
  - Output: `web/data/{codec}/syntax.json`

- **Semantics Extraction**: AI-powered extraction of parameter semantics
  - Location: `scripts/extract_semantics_with_ai.py`
  - Output: `web/data/{codec}/semantics.json`
  - Status: 423 parameters with semantics for VVC

- **Connection Analysis**: AI-generated parameter dependency and relationship mapping
  - Location: `scripts/generate_connections_simple.py`
  - Output: `web/data/{codec}/connections.json`
  - Status: 423 parameters with connection data

### 3. User Interface Components

#### A. Syntax Navigator (Left Sidebar)
- Hierarchical list of all syntax structures
- Search functionality to filter syntax structures
- Section badges showing specification section numbers
- Click to view syntax details

#### B. Syntax Display (Main Panel)
- Displays syntax structure in formatted code blocks
- Shows clickable parameters that link to semantics
- Supports function calls with parentheses (e.g., `slice_header()`)
- Section reference display

#### C. Semantics Modal
- **Parameter Semantics Display**:
  - Parameter name and description
  - Source specification section
  - Detailed semantic information

- **Navigation Features**:
  - Back button for navigation history
  - Clickable cross-references to other parameters

- **AI Analysis**:
  - AI-powered explanation button (robot icon)
  - Context-aware explanations via Claude API
  - Inline display of AI analysis
  - **Syntax-specific caching** (LATEST):
    - Each syntax structure gets its own cached analysis per parameter
    - Cache keys include: codec + syntax context + parameter name
    - Visual indicators: cache status badge, syntax context badge, timestamp
    - Re-run button to refresh analysis
    - Persistent storage via localStorage

- **Connection Visualization** (LATEST):
  - ✅ Removed list-based Dependencies/References/Related Concepts
  - ✅ Direct inline D3.js force-directed graph
  - ✅ No "View Graph" button needed - shows automatically
  - ✅ Interactive nodes (click to navigate to parameter)
  - ✅ Color-coded connection types:
    - Pink: Root node (selected parameter)
    - Purple: Level 1 connections
    - Blue: Level 2 connections
  - ✅ Arrow markers showing connection direction
  - ✅ Zoom and pan support
  - ✅ Drag nodes to rearrange

### 4. Data Files Status

#### VVC (H.266) Dataset:
- **Syntax**: ✅ Complete (all syntax structures extracted)
- **Semantics**: ✅ 423 parameters with AI-generated semantics
- **Connections**: ✅ 423 parameters with connection data
  - Dependencies (what this parameter depends on)
  - References (what this parameter references)
  - Related concepts (conceptually similar parameters)

#### HEVC (H.265) & AVC (H.264):
- Status: Data structure ready, awaiting extraction

---

## 🚧 Known Issues

### 1. **CRITICAL: Incorrect Semantics Mapping**
- **Issue**: Some syntax structures are showing wrong semantics
- **Impact**: Users see incorrect parameter descriptions
- **Status**: 🔴 NEEDS INVESTIGATION
- **Next Steps**:
  - Verify syntax.json parameter names match semantics.json keys
  - Check for parameter name variations (underscores, spaces, etc.)
  - One-by-one verification of all mappings

### 2. Parameter Clickability
- **Issue**: Some function calls with spaces (e.g., `slice_header( )`) may not be clickable
- **Status**: ⚠️ Partially resolved - needs testing

### 3. Connection Graph Performance
- **Issue**: Large graphs with many connections may be slow to render
- **Status**: ⚠️ Monitor performance

---

## 📁 Project Structure

```
interactive-hls/
├── web/
│   ├── index.html              # Main application
│   ├── login.html              # Authentication page
│   ├── css/
│   │   └── style.css           # Application styles
│   ├── js/
│   │   ├── app.js              # Main application logic
│   │   ├── connection-graph.js # D3.js graph visualization
│   │   └── connection-tree.js  # Tree visualization (legacy)
│   ├── data/
│   │   ├── vvc/
│   │   │   ├── syntax.json     # VVC syntax structures
│   │   │   ├── semantics.json  # VVC parameter semantics
│   │   │   └── connections.json # VVC parameter connections
│   │   ├── hevc/               # HEVC data (pending)
│   │   └── avc/                # AVC data (pending)
│   └── config.json             # API key configuration
├── server/
│   └── proxy.py                # Flask API proxy
├── scripts/
│   ├── extract_syntax.py       # Extract syntax from PDF
│   ├── extract_semantics_with_ai.py  # AI-powered semantics extraction
│   └── generate_connections_simple.py # Generate parameter connections
└── specs/                      # Specification PDF files
```

---

## 🔧 Recent Changes (Current Session)

### Session 1 - Connection Graph Implementation:
1. Fixed duplicate `connectionsData` variable declaration
2. Resolved JavaScript syntax error preventing app load
3. Implemented inline D3.js connection graph
4. Removed dependency/reference/related concept lists
5. Removed "View Graph" button requirement
6. Fixed node clickability (`showParameterSemantics` → `displaySemantics`)
7. Added CSS styling for inline graph container

### Session 2 - Syntax-Specific AI Analysis Caching:
1. Updated cache key generation to include syntax context
2. Modified `getAiCacheKey()` to accept `syntaxContext` parameter
3. Updated `loadCachedAnalysis()` to use syntax-specific cache keys
4. Modified `saveCachedAnalysis()` to store syntax context in cache data
5. Reorganized `aiExplainParameter()` flow to find syntax context earlier
6. Added syntax context badge to UI display
7. Added CSS styling for syntax context badge

### Files Modified:
- **Session 1:**
  - `web/js/app.js` (lines 10, 691-793)
  - `web/js/connection-graph.js` (line 162)
  - `web/css/style.css` (lines 1323-1331)
- **Session 2:**
  - `web/js/app.js` (lines 1120-1312)
  - `web/css/style.css` (lines 1003-1018)

---

## 🎯 Next Priority Tasks

1. **URGENT**: Investigate and fix incorrect semantics mapping
   - Compare syntax.json parameters with semantics.json keys
   - Identify mismatched mappings
   - Verify parameter name consistency
   - Fix mapping logic in app.js

2. Test connection graph with various parameters
3. Optimize graph rendering for large connection sets
4. Extract HEVC and AVC data
5. Improve AI analysis prompts for better explanations

---

## 🚀 Future Enhancements

- Export functionality (PDF/JSON reports)
- Custom annotation system
- Comparison tool between codecs
- Search across semantics content
- Graph visualization improvements (clustering, filtering)
- Mobile responsive design
- Dark mode support

---

## 📊 Statistics

- **Total VVC Parameters**: 423
- **Parameters with Semantics**: 423 (100%)
- **Parameters with Connections**: 423 (100%)
- **Average Connections per Parameter**: ~8-12
- **Syntax Structures**: ~50+ major structures
- **Specification Sections Covered**: All major HLS sections

---

## 🛠️ Development Commands

```bash
# Start proxy server
cd server && python proxy.py

# Start web server
cd web && python -m http.server 8000

# Extract syntax
python scripts/extract_syntax.py

# Extract semantics with AI
python scripts/extract_semantics_with_ai.py

# Generate connections
python scripts/generate_connections_simple.py --codec vvc
```

---

Last Updated: 2026-03-19
