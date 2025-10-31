# 🎯 COMMANDS TO RUN - Quick Reference

## First Time Setup

### Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="your-openai-api-key-here"
cd ..
```

### Frontend Setup
```powershell
cd frontend
npm install
cd ..
```

---

## Running the Application (Every Time)

### Method 1: Two Separate Terminals

**TERMINAL 1 - Backend (Port 8000):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY="your-openai-api-key-here"
python start.py
```
✅ Backend API: http://localhost:8000
✅ API Docs: http://localhost:8000/docs

**TERMINAL 2 - Frontend (Port 3000):**
```powershell
cd frontend
npm start
```
✅ Frontend UI: http://localhost:3000

---

### Method 2: Automated Startup (Both Servers)

**Using PowerShell Script:**
```powershell
.\start_all.ps1
```

**Using Batch File:**
```cmd
start_all.bat
```

This opens 2 terminal windows automatically.

---

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main UI - ASL Translation Interface |
| **Backend API** | http://localhost:8000 | REST API Server |
| **API Docs** | http://localhost:8000/docs | Interactive API Documentation |
| **Health Check** | http://localhost:8000/health | Backend Status |

---

## Quick Commands

### Stop Servers
- Press `Ctrl + C` in each terminal window

### Restart Backend
```powershell
# In backend terminal:
# Press Ctrl+C, then:
python start.py
```

### Restart Frontend
```powershell
# In frontend terminal:
# Press Ctrl+C, then:
npm start
```

### Check if Ports are in Use
```powershell
# Check port 8000 (backend)
netstat -ano | findstr :8000

# Check port 3000 (frontend)
netstat -ano | findstr :3000
```

### Kill Process on Port
```powershell
# Find PID from netstat output, then:
taskkill /PID <PID_NUMBER> /F
```

---

## Development Mode

### Backend (with auto-reload)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (with auto-reload)
```powershell
cd frontend
npm run dev  # Uses nodemon
```

---

## Environment Variables

### Set OpenAI API Key (Required)

**Temporary (this session only):**
```powershell
$env:OPENAI_API_KEY="sk-..."
```

**Permanent (all sessions):**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')
```

Restart terminal after setting permanent variable.

---

## Testing

### Test Backend Health
```powershell
Invoke-RestMethod http://localhost:8000/health
```

Expected: `{"status":"ok","model_loaded":true}`

### Test Frontend Loading
Open browser: http://localhost:3000

### Test Camera Access
1. Open http://localhost:3000
2. Click "Start Inference"
3. Allow camera permissions
4. Verify video feed appears

---

## Common Issues & Fixes

### ❌ "Python not found"
```powershell
# Install Python 3.10+ from python.org
python --version  # Should show 3.10 or higher
```

### ❌ "npm not found"
```powershell
# Install Node.js from nodejs.org
node --version    # Should show 16.0 or higher
npm --version
```

### ❌ "Port already in use"
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in backend/start.py or frontend/server.js
```

### ❌ "Virtual environment not activated"
```powershell
cd backend
.\venv\Scripts\Activate.ps1
# You should see (venv) in prompt
```

### ❌ "CORS errors in browser"
- Ensure backend is running on port 8000
- Check browser console for specific error
- Verify `window.API_BASE_URL` in HTML files

### ❌ "Model not found"
```powershell
# Check if model files exist
ls backend\pretrained\gesture_model.pkl
ls backend\pretrained\letter_model.pkl

# If missing, you need to train or obtain models
```

---

## File Locations

```
MUJ REPO/
├── backend/
│   ├── start.py          ← Start backend server
│   ├── requirements.txt  ← Python dependencies
│   └── app/main.py       ← FastAPI application
├── frontend/
│   ├── server.js         ← Express server
│   ├── package.json      ← Node.js dependencies
│   └── templates/        ← HTML files
├── start_all.ps1         ← Auto-start both (PowerShell)
└── start_all.bat         ← Auto-start both (CMD)
```

---

## 🎉 Ready to Start?

**Run these 2 commands in separate terminals:**

```powershell
# Terminal 1:
cd backend; .\venv\Scripts\Activate.ps1; python start.py

# Terminal 2:
cd frontend; npm start
```

Then open: **http://localhost:3000**

---

📚 **More Help**: See `QUICK_START_GUIDE.md` for detailed troubleshooting
