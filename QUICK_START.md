# 🚀 Quick Start Guide

Get the Sign Language Translator running in 5 minutes!

## Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)
- OpenAI API Key

## Option 1: Quick Local Setup (5 minutes)

### Step 1: Navigate to Backend
```bash
cd backend
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Environment Variable
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here
```

### Step 4: Start the Server
```bash
python start.py
```

### Step 5: Open Browser
```
http://localhost:8000
```

**That's it! 🎉**

---

## Option 2: Docker Setup (3 minutes)

### Step 1: Setup Environment
```bash
cd deployment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Step 2: Start Services
```bash
docker-compose up -d
```

### Step 3: Open Browser
```
http://localhost
```

**Done! 🎉**

---

## 🧪 Quick Test

### Test API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "model_loaded": true}
```

### Test Model Status
```bash
curl http://localhost:8000/model-status
```

### View API Documentation
Open in browser:
```
http://localhost:8000/docs
```

---

## 🎯 Quick Feature Demo

### 1. Gesture Detection
1. Navigate to: `http://localhost:8000/`
2. Click "Enable Camera"
3. Show hand gestures
4. See real-time detection!

### 2. Classroom Mode
1. Teacher goes to: `http://localhost:8000/teacher`
2. Note the room ID (e.g., ABC123)
3. Student goes to: `http://localhost:8000/student?room_id=ABC123`
4. Teacher speaks → Students see sign video!

### 3. Video Generation
1. Navigate to: `http://localhost:8000/learn`
2. Type: "Hello World"
3. Click "Translate"
4. Watch the generated sign language video!

---

## 🐛 Quick Troubleshooting

### Issue: "Module not found"
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Model not loaded"
**Solution:** Copy model files to `backend/pretrained/`:
- `gesture_model.pkl`
- `letter_model.pkl`

### Issue: "Port already in use"
**Solution:** Change port in start command:
```bash
uvicorn app.main:app --port 8001
```

### Issue: Docker build fails
**Solution:**
```bash
cd deployment
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Next Steps

- ✅ Check out `README.md` for full documentation
- ✅ Read `DEPLOYMENT_GUIDE.md` for production deployment
- ✅ See `MIGRATION_GUIDE.md` for Flask→FastAPI changes
- ✅ Review `VERIFICATION_CHECKLIST.md` before deploying

---

## 🆘 Need Help?

1. Check logs:
   ```bash
   # Docker
   docker-compose logs -f backend
   
   # Direct run
   # Check terminal output
   ```

2. Test endpoints:
   ```bash
   python backend/test_backend.py
   ```

3. Review documentation:
   - API Docs: http://localhost:8000/docs
   - README: `README.md`
   - Deployment Guide: `deployment/DEPLOYMENT_GUIDE.md`

---

## 🎉 Success!

You should now have:
- ✅ Backend running on port 8000
- ✅ API documentation at /docs
- ✅ All endpoints functional
- ✅ WebSocket support enabled
- ✅ Ready for sign language translation!

**Enjoy your Sign Language Translator! 🤟**

---

**Quick Links:**
- Homepage: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Classroom: http://localhost:8000/classroom
