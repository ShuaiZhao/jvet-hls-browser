# Migration to Port 8000 - Combined Server

## Summary

We've created a **new combined server** that runs on port 8000 and eliminates the need for multiple servers!

## What Changed?

### Before (Port 8001 - Not Working)
```
┌─────────────────────┐
│  Static Web Server  │  Port 8000 (python -m http.server)
└─────────────────────┘
           +
┌─────────────────────┐
│  Claude API Proxy   │  Port 8001 (server/proxy.py)
└─────────────────────┘

Problem: Port 8001 wasn't working, needed 2 servers, CORS issues
```

### After (Port 8000 - New Combined Server)
```
┌─────────────────────────────────────┐
│     Combined Server (Port 8000)     │
│  • Static Files (HTML/CSS/JS/JSON)  │
│  • Claude API Proxy (/api/claude)   │
│  • Health Check (/api/health)       │
└─────────────────────────────────────┘

Solution: One server, no CORS, works perfectly!
```

## Files Changed

### 1. New Combined Server
**File:** `server/combined_server.py`
- Serves static files from `web/` directory
- Handles `/api/claude` proxy requests
- Runs on port 8000
- Auto-restart capable

### 2. Frontend Update
**File:** `web/js/app.js` (line 1229)

**Before:**
```javascript
const response = await fetch('http://localhost:8001/api/claude', {
```

**After:**
```javascript
const response = await fetch('/api/claude', {
```

Changed to **relative URL** - automatically uses the same port as the web page (8000).

### 3. Startup Scripts Updated
**Files:** `start_server.sh`, `start_server.bat`
- Added option 1: Combined Server (recommended)
- Kept option 2: Proxy Server (legacy, port 8001)
- Kept option 3: Backend API Server (advanced, port 5000)

### 4. New Documentation
- **QUICK_START.md** - 2-minute setup guide
- **Updated SERVER_GUIDE.md** - Combined server details
- **This file** - Migration guide

## How to Use

### Quick Start (Recommended)

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Start server
./start_server.sh
# Choose option 1 (Combined Server)

# 3. Open browser
# http://localhost:8000
```

### Direct Start

```bash
python server/combined_server.py
```

## Benefits of Combined Server

| Benefit | Description |
|---------|-------------|
| **One Port** | Everything on port 8000 |
| **No CORS** | Same-origin requests |
| **Simpler** | One command to start |
| **Faster** | No proxy overhead |
| **Reliable** | Fewer moving parts |
| **Auto-restart** | Built into startup script |

## Migration Checklist

If you were using the old port 8001 setup:

- [x] ✅ Combined server created (`server/combined_server.py`)
- [x] ✅ Frontend updated to use relative URLs
- [x] ✅ Startup scripts updated
- [x] ✅ Documentation updated
- [x] ✅ Port 8000 now handles everything

**Action Required:**
1. Stop any existing servers (port 8000 and 8001)
2. Use the new combined server on port 8000
3. Enjoy simplified setup!

## Backward Compatibility

The old servers still work if you need them:

**Port 8001 (Proxy Server):**
```bash
python server/proxy.py
```

**Port 5000 (Backend API Server):**
```bash
python web/backend/api_server.py
```

But we **recommend using port 8000 combined server** for simplicity.

## Troubleshooting

### "Port 8000 already in use"

Kill existing process:
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "API calls fail"

Check that:
1. Server is running on port 8000
2. API key is set correctly
3. You're accessing via http://localhost:8000 (not file://)

### "Static files not loading"

The combined server automatically serves from `web/` directory. Make sure:
1. Files exist in `web/` folder
2. Paths are correct (no leading slash issues)
3. Server has read permissions

## Testing

### Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "api_key_configured": true,
  "static_files": "/path/to/web",
  "server_type": "combined"
}
```

### Static Files
```bash
curl http://localhost:8000/
# Should return login.html

curl http://localhost:8000/index.html
# Should return main application

curl http://localhost:8000/js/app.js
# Should return JavaScript file
```

### API Proxy
```bash
curl -X POST http://localhost:8000/api/claude \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Summary

✅ **Port 8000 combined server** solves all the issues:
- Port 8001 not working → Use port 8000
- Multiple servers → One server
- CORS issues → Same-origin requests
- Complex setup → Simple startup

🎉 **Result:** Easier to use, more reliable, simpler to deploy!

For help, see:
- **QUICK_START.md** - Fast setup guide
- **SERVER_GUIDE.md** - Detailed server documentation
- **README.md** - Complete project documentation
