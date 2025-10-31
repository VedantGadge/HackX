# 🚀 Quick Start Guide - Running Frontend & Backend

This guide will help you run both the frontend and backend servers for local development.

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10+ installed
- ✅ Node.js 16+ installed
- ✅ npm installed
- ✅ OpenAI API key (for LLM features)

## Step-by-Step Setup

### 1️⃣ Setup Backend (First Time Only)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
$env:OPENAI_API_KEY="your-api-key-here"

# Go back to root
cd ..
```

### 2️⃣ Setup Frontend (First Time Only)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Go back to root
cd ..
```

### 3️⃣ Running Both Servers

#### Option A: Run Individually (2 Terminals)

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY="your-api-key-here"
python start.py
```
✅ Backend running at: http://localhost:8000

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```
✅ Frontend running at: http://localhost:3000

#### Option B: Use Startup Scripts (Windows)

**PowerShell:**
```powershell
.\start_all.ps1
```

**Command Prompt:**
```cmd
start_all.bat
```

This will open 2 terminal windows automatically.

## 🎯 Access the Application

1. **Open Browser**: Navigate to http://localhost:3000
2. **Main Features**:
   - Real-time ASL detection
   - Video translation (English → ASL)
   - Learning mode
   - Classroom feature

3. **API Documentation**: http://localhost:8000/docs

## 🔧 Verification Steps

### Check Backend Health
```powershell
# In PowerShell or browser
Invoke-RestMethod http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### Check Frontend
Open http://localhost:3000 in your browser. You should see the main interface.

### Test Camera Access
1. Click "Start Inference" button
2. Allow camera permissions
3. Verify video feed appears

### Test API Connection
Open browser DevTools (F12) → Console. You should see:
```
Model Status: {demo_mode: false, model_loaded: true, ...}
```

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError`
```powershell
# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

**Issue**: `Model file not found`
```powershell
# Ensure model files exist
ls backend\pretrained\gesture_model.pkl
ls backend\pretrained\letter_model.pkl
```

**Issue**: Port 8000 already in use
```powershell
# Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues

**Issue**: `npm: command not found`
```powershell
# Install Node.js from https://nodejs.org/
# Restart terminal after installation
```

**Issue**: Port 3000 already in use
```powershell
# Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or change port in frontend/server.js:
# const PORT = 3001;
```

**Issue**: CORS errors in browser console
- Ensure backend is running on port 8000
- Check `window.API_BASE_URL` in index.html matches backend URL

### Camera Issues

**Issue**: Camera not detected
- Check browser permissions (click lock icon in address bar)
- Ensure no other app is using the camera
- Try in Chrome/Edge (best compatibility)

**Issue**: `NotAllowedError: Permission denied`
- Allow camera access when prompted
- Check browser settings → Privacy → Camera

## 🎨 Development Workflow

### Making Backend Changes
1. Edit files in `backend/`
2. Restart backend server (Ctrl+C, then `python start.py`)
3. Test changes at http://localhost:8000

### Making Frontend Changes
1. Edit files in `frontend/static/` or `frontend/templates/`
2. Refresh browser (no restart needed for HTML/CSS/JS)
3. For server.js changes: Restart with `npm start`

### Using Hot Reload (Frontend)
```powershell
cd frontend
npm run dev  # Uses nodemon for auto-restart
```

## 📝 Common Commands Reference

### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1              # Activate env
python start.py                          # Start server
pytest tests/                            # Run tests
python test_backend.py                   # Test API endpoints
```

### Frontend
```powershell
cd frontend
npm install                              # Install deps
npm start                                # Start server
npm run dev                              # Start with hot reload
```

### Environment
```powershell
# Set OpenAI key (temporary)
$env:OPENAI_API_KEY="sk-..."

# Set permanently (Windows)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')
```

## 🚀 Next Steps

Once both servers are running:

1. **Test Real-time Detection**:
   - Go to http://localhost:3000
   - Click "Start Inference"
   - Make ASL gestures to camera

2. **Test Video Translation**:
   - Scroll to "Reverse Translation" section
   - Enter text like "Hello world"
   - Click "Translate to ASL Video"

3. **Explore Other Features**:
   - Learning mode: http://localhost:3000/learn
   - Classroom: http://localhost:3000/classroom

4. **API Testing**:
   - Visit http://localhost:8000/docs
   - Try out API endpoints interactively

## 📚 Additional Resources

- [Frontend README](frontend/README.md)
- [Backend README](backend/README.md)
- [API Documentation](backend/API_DOCUMENTATION.md)
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)

## 🆘 Still Having Issues?

1. Check both terminals for error messages
2. Verify all prerequisites are installed
3. Ensure ports 3000 and 8000 are free
4. Try closing and reopening terminals
5. Check firewall/antivirus settings

---

**Ready to Go?** Run `.\start_all.ps1` and open http://localhost:3000! 🎉
