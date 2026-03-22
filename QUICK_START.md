# Quick Start Guide - Interactive HLS Browser

Get up and running in **2 minutes**!

## Step 1: Set API Key

```bash
# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Windows
set ANTHROPIC_API_KEY=sk-ant-api03-...
```

Get your API key at: https://console.anthropic.com/

## Step 2: Start Server

### Option A: Using Startup Script (Recommended)

**macOS/Linux:**
```bash
./start_server.sh
# Choose option 1 (Combined Server)
```

**Windows:**
```cmd
start_server.bat
REM Choose option 1 (Combined Server)
```

### Option B: Direct Start

```bash
python server/combined_server.py
```

## Step 3: Open Browser

Open: **http://localhost:8000**

Login with:
- Username: `admin`
- Password: `admin_password`

## Done! 🎉

You should now see the Interactive HLS Specification Browser.

---

## What Just Happened?

The **Combined Server** (port 8000) provides:
- ✅ Static web files (HTML/CSS/JS)
- ✅ Claude AI proxy for analysis
- ✅ All in one server - no multiple ports!

---

## Troubleshooting

### "API key not configured"

Make sure you set the environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or create `web/config.json`:
```json
{
  "anthropic_api_key": "sk-ant-..."
}
```

### "Port 8000 already in use"

Kill the existing process:
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Server keeps crashing?

The startup script will auto-restart. Check the error messages for:
- Invalid API key
- Missing dependencies (`pip install -r requirements.txt`)
- Network connectivity issues

---

## What's Different from Port 8001?

| Feature | Port 8001 (Old) | Port 8000 (New) |
|---------|-----------------|-----------------|
| **Static Files** | ❌ Separate server needed | ✅ Built-in |
| **AI Proxy** | ✅ Yes | ✅ Yes |
| **Servers to Run** | 2 servers | 1 server |
| **CORS Issues** | Sometimes | Never |
| **Easier Setup** | ❌ No | ✅ Yes |

**Recommendation:** Use port 8000 (combined server) for simplicity!

---

## Next Steps

1. **Browse Syntax Structures** - Click any syntax on the left
2. **View Parameter Details** - Click any parameter name
3. **See Connections** - Automatic D3.js graph visualization
4. **AI Analysis** - Click the robot icon for AI explanations

Enjoy exploring video codec specifications! 🎬
