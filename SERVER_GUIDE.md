# Server Management Guide

## ⭐ NEW: Combined Server (Port 8000) - RECOMMENDED

We now have a **single combined server** that does everything:
- ✅ Serves static web files (HTML/CSS/JS)
- ✅ Handles Claude AI proxy requests
- ✅ No need for multiple servers or ports!

**Quick Start:**
```bash
./start_server.sh  # Choose option 1
# or
python server/combined_server.py
```

Then open: **http://localhost:8000**

---

## Why Servers Stop

The servers were stopping due to several issues that have now been **fixed**:

### Problems Identified (FIXED)
1. ✅ **Debug Mode** - Was causing auto-restart on code changes
2. ✅ **No Timeout Handling** - Long API calls would hang indefinitely
3. ✅ **Poor Error Handling** - Exceptions would crash the entire server
4. ✅ **No Auto-Restart** - Server wouldn't recover from crashes
5. ✅ **CORS Issues** - Preflight requests weren't handled properly

### Improvements Made

#### 1. Stable Server Configuration
- ✅ Disabled debug mode (`debug=False`)
- ✅ Added threaded support for multiple concurrent requests
- ✅ Disabled auto-reloader to prevent unexpected restarts
- ✅ Added 60-second timeout for Claude API calls

#### 2. Better Error Handling
- ✅ Specific exception handling for API timeouts
- ✅ Detailed error logging with stack traces
- ✅ Graceful error responses instead of crashes
- ✅ JSON parsing error handling

#### 3. Auto-Restart Scripts
- ✅ Created `start_server.sh` (macOS/Linux)
- ✅ Created `start_server.bat` (Windows)
- ✅ Automatic restart on crash with 3-second delay
- ✅ API key validation before starting

---

## Quick Start

### Option 1: Using Startup Scripts (Recommended)

**macOS/Linux:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Windows:**
```cmd
start_server.bat
```

The script will:
- Check for API key
- Activate virtual environment
- Show menu to choose server
- Auto-restart on crash
- Clean shutdown on CTRL+C

### Option 2: Manual Start

**Proxy Server (port 8001):**
```bash
python server/proxy.py
```

**Backend API Server (port 5000):**
```bash
python web/backend/api_server.py
```

---

## Server Details

### 1. Combined Server (`server/combined_server.py`) ⭐ RECOMMENDED

**Purpose:** All-in-one server for static files + Claude API proxy

**Port:** 8000

**Endpoints:**
- `GET /` - Login page
- `GET /index.html` - Main application
- `GET /<path>` - Static files (CSS, JS, JSON, etc.)
- `POST /api/claude` - Claude API proxy
- `GET /api/health` - Health check

**Configuration:**
- 60-second timeout for API calls
- Threaded for concurrent requests
- Serves files from `web/` directory
- Automatic directory index support

**Advantages:**
- ✅ One server instead of two
- ✅ No CORS issues (same origin)
- ✅ Simpler to deploy
- ✅ Easier for users to run

**Usage:**
```bash
python server/combined_server.py
# Open http://localhost:8000
```

### 2. Proxy Server (`server/proxy.py`) - Legacy

**Purpose:** CORS proxy for Claude API calls from browser

**Port:** 8001

**Endpoints:**
- `POST /api/claude` - Proxy Claude API requests
- `GET /health` - Health check

**Configuration:**
- 60-second timeout for API calls
- Threaded for concurrent requests
- Detailed error logging

**Usage:**
```javascript
fetch('http://localhost:8001/api/claude', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 1024,
        messages: [{role: 'user', content: 'Hello'}]
    })
})
```

### 2. Backend API Server (`web/backend/api_server.py`)

**Purpose:** Real-time parameter analysis and search

**Port:** 5000

**Endpoints:**
- `POST /api/analyze-parameter` - Analyze parameter relationships
- `POST /api/search` - Semantic search
- `GET /api/health` - Health check

**Configuration:**
- 60-second timeout for analysis
- Loads codec data on demand
- Caches loaded data in memory

**Usage:**
```javascript
fetch('http://localhost:5000/api/analyze-parameter', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        codec: 'vvc',
        parameter: 'sps_chroma_format_idc'
    })
})
```

---

## Troubleshooting

### Server Won't Start

**Problem:** `ANTHROPIC_API_KEY not set`

**Solution:**
```bash
# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Windows
set ANTHROPIC_API_KEY=sk-ant-api03-...
```

Or create `web/config.json`:
```json
{
  "ANTHROPIC_API_KEY": "sk-ant-api03-..."
}
```

---

### Server Stops After Request

**Problem:** Server crashes on certain requests

**Solution:** Check server logs for errors. Common issues:
- Invalid API key → Set correct key
- Rate limiting → Wait and try again
- Network issues → Check internet connection

The server will now auto-restart after crashes!

---

### Timeout Errors

**Problem:** `Request timed out. Please try again.`

**Solution:**
- Claude API took too long (>60 seconds)
- This is normal for complex analyses
- Try again - subsequent requests may be faster
- The timeout prevents server hangs

---

### Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using the port
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

---

### CORS Errors in Browser

**Problem:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
- Make sure proxy server is running on port 8001
- Check browser console for exact error
- Verify fetch URL is correct: `http://localhost:8001`
- Try clearing browser cache

---

## Production Deployment

### For Production Use

Replace Flask development server with production WSGI server:

**Using Gunicorn (Linux/macOS):**
```bash
pip install gunicorn

# Proxy server
gunicorn -w 4 -b 0.0.0.0:8001 server.proxy:app

# Backend server
gunicorn -w 4 -b 0.0.0.0:5000 web.backend.api_server:app
```

**Using Waitress (Windows):**
```bash
pip install waitress

# Proxy server
waitress-serve --host=0.0.0.0 --port=8001 server.proxy:app

# Backend server
waitress-serve --host=0.0.0.0 --port=5000 web.backend.api_server:app
```

### Environment Variables

Required:
- `ANTHROPIC_API_KEY` - Your Claude API key

Optional:
- `FLASK_ENV=production` - Production mode
- `PORT` - Override default port

---

## Server Logs

### Enable Verbose Logging

Both servers now print detailed error information:

```python
# In server code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Redirect output to log file:

```bash
# macOS/Linux
python server/proxy.py > server.log 2>&1 &

# Windows
python server\proxy.py > server.log 2>&1
```

---

## Performance Tips

### 1. Use Caching
The frontend already caches AI analysis results in localStorage. This reduces server load.

### 2. Rate Limiting
Claude API has rate limits. The servers handle this with:
- 60-second timeouts
- Graceful error messages
- Auto-retry capability in startup script

### 3. Connection Pooling
For production, use a proper WSGI server (Gunicorn/Waitress) which handles connection pooling automatically.

### 4. Monitor Resources
```bash
# Check server resource usage
top -p <PID>  # Linux
top | grep python  # macOS
tasklist | findstr python  # Windows
```

---

## API Key Security

### Development
- Use environment variables (not hardcoded)
- Don't commit config.json to git
- Use .gitignore to exclude sensitive files

### Production
- Use secret management service (AWS Secrets Manager, etc.)
- Rotate keys periodically
- Monitor API usage
- Set up billing alerts

---

## Testing Servers

### Health Check
```bash
# Proxy server
curl http://localhost:8001/health

# Backend server
curl http://localhost:5000/api/health
```

### Test Request
```bash
# Proxy server
curl -X POST http://localhost:8001/api/claude \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-5-20250929","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}'

# Backend server
curl -X POST http://localhost:5000/api/analyze-parameter \
  -H "Content-Type: application/json" \
  -d '{"codec":"vvc","parameter":"sps_seq_parameter_set_id"}'
```

---

## Summary

✅ **Servers are now stable** with:
- Production-ready configuration
- Auto-restart on crash
- 60-second API timeouts
- Better error handling
- Detailed logging

✅ **Easy to start** with:
- Simple startup scripts
- Menu-driven interface
- API key validation
- Virtual environment support

✅ **Easy to debug** with:
- Stack traces on errors
- Health check endpoints
- Request logging
- Clear error messages

For additional help, check the main README.md or open a GitHub issue.
