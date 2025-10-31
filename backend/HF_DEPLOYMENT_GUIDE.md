# 🚀 Hugging Face Spaces Deployment Guide

## Space Information
- **Space URL**: https://huggingface.co/spaces/Lamaq/signlink-hackx
- **Space Name**: signlink-hackx
- **Owner**: Lamaq
- **SDK**: Docker
- **Port**: 8000

---

## 📋 Quick Deploy Steps

### Option 1: Automated Deployment (Recommended)

**For Windows (PowerShell):**
```powershell
cd backend
.\deploy_to_hf.ps1
```

**For Linux/Mac (Bash):**
```bash
cd backend
chmod +x deploy_to_hf.sh
./deploy_to_hf.sh
```

### Option 2: Manual Deployment via Git

#### Step 1: Clone the Space Repository
```bash
git clone https://huggingface.co/spaces/Lamaq/signlink-hackx
cd signlink-hackx
```

#### Step 2: Copy Backend Files
Copy these files/folders from your backend directory:
- ✅ `app/` - Main application code
- ✅ `services/` - Service modules (revtrans, video_fetcher)
- ✅ `utils/` - Utility functions
- ✅ `models/` - Model definitions
- ✅ `pretrained/` - ML model files (.pkl)
- ✅ `mapper/` - WLASL JSON mapper
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Container configuration
- ✅ `README.md` - Space documentation
- ✅ `start.py` - Application starter
- ✅ `.dockerignore` - Docker ignore rules

#### Step 3: Create Empty Directories
```bash
mkdir -p outputs videos
```

#### Step 4: Commit and Push
```bash
git add .
git commit -m "Deploy SignLink backend"
git push
```

**Authentication:**
- Username: `Lamaq`
- Password: Your Hugging Face **Access Token** (not your password!)
- Get token: https://huggingface.co/settings/tokens

---

## 🔐 Environment Variables Setup

### Step 1: Go to Space Settings
https://huggingface.co/spaces/Lamaq/signlink-hackx/settings

### Step 2: Navigate to "Variables and secrets"

### Step 3: Add Secret
- **Name**: `OPENAI_API_KEY`
- **Value**: Your OpenAI API key (starts with `sk-...`)
- Click **Save**

⚠️ **Critical**: Without this environment variable, LLM features (transcription, gloss conversion) will not work!

---

## 🏗️ Build Process

### What Happens After Push:
1. **Upload**: Files are uploaded to Hugging Face
2. **Build**: Docker image is built (5-10 minutes)
3. **Deploy**: Container starts and runs
4. **Ready**: Space becomes accessible

### Monitor Build:
- Go to: https://huggingface.co/spaces/Lamaq/signlink-hackx
- Check "Logs" tab for build progress
- Look for: `INFO:     Application startup complete.`

---

## ✅ Verify Deployment

### Test Health Endpoint
```bash
curl https://lamaq-signlink-hackx.hf.space/health
```

**Expected Response:**
```json
{"status": "ok", "model_loaded": true}
```

### Test Model Status
```bash
curl https://lamaq-signlink-hackx.hf.space/model-status
```

### Access API Documentation
Open in browser:
```
https://lamaq-signlink-hackx.hf.space/docs
```

---

## 🔧 Update Frontend Configuration

### Update All Frontend Files

**In `frontend/templates/index.html`:**
```html
<script>
    window.API_BASE_URL = 'https://lamaq-signlink-hackx.hf.space';
</script>
```

**In `frontend/templates/teacher.html`:**
```html
<script>
    window.API_BASE_URL = 'https://lamaq-signlink-hackx.hf.space';
</script>
```

**In `frontend/templates/student.html`:**
```html
<script>
    window.API_BASE_URL = 'https://lamaq-signlink-hackx.hf.space';
</script>
```

**In `frontend/static/script.js`:**
```javascript
const API_BASE_URL = window.API_BASE_URL || 'https://lamaq-signlink-hackx.hf.space';
```

---

## 🧩 Update Chrome Extension

**In `chrome_extension/content.js`:**
```javascript
let backendUrl = 'https://lamaq-signlink-hackx.hf.space';
```

**In `frontend/chrome_extension/content.js`:**
```javascript
let backendUrl = 'https://lamaq-signlink-hackx.hf.space';
```

---

## 📊 API Endpoints Available

Once deployed, these endpoints will be accessible:

### Core
- `GET /` - API information
- `GET /health` - Health check
- `GET /model-status` - Model status
- `GET /docs` - API documentation (Swagger)

### Inference
- `POST /infer-frame` - Gesture detection
- `POST /infer-letter` - Letter detection

### Video Translation
- `POST /reverse-translate-video` - Generate ASL video
- `POST /process-confirmed-words` - Gloss to English

### Chrome Extension
- `POST /tokenize-text` - Tokenize captions
- `GET /token-video/{token}` - Get token video

### Classroom (WebSocket)
- `WS /ws/classroom/{room_id}/teacher` - Teacher connection
- `WS /ws/classroom/{room_id}/student` - Student connection

### Static Files
- `GET /outputs/{filename}` - Generated video files

---

## 🐛 Troubleshooting

### Build Fails
**Check Dockerfile:**
- Ensure all COPY commands reference existing files
- Verify requirements.txt has correct package versions

**Check Logs:**
- Go to Space page → Logs tab
- Look for error messages during build

### Space Not Starting
**Common Issues:**
1. Missing environment variables (OPENAI_API_KEY)
2. Port mismatch (must be 8000)
3. Model files too large or missing

**Solution:**
- Check Space settings for environment variables
- Review logs for specific errors
- Ensure pretrained/ folder has model files

### API Returns Errors
**Model Not Loading:**
```json
{"error": "Model not loaded"}
```
**Solution:** Check that `pretrained/gesture_model.pkl` and `letter_model.pkl` exist

**OpenAI Errors:**
```json
{"error": "OPENAI_API_KEY not set"}
```
**Solution:** Add OPENAI_API_KEY in Space settings

### CORS Issues
**Frontend can't connect:**
- Ensure CORS is enabled in `main.py`
- Check browser console for specific errors
- Verify API_BASE_URL is correct in frontend

---

## 📈 Monitoring

### Check Space Status
- Go to: https://huggingface.co/spaces/Lamaq/signlink-hackx
- Status indicator: 🟢 Running | 🔴 Building | ⚪ Stopped

### View Logs
- Click "Logs" tab on Space page
- Monitor real-time application logs
- Check for errors or warnings

### Performance
- Free tier has usage limits
- Consider upgrading for production use
- Monitor response times and errors

---

## 🔄 Update Deployment

### To Update the Space:

1. **Make changes** in your local backend code
2. **Test locally** to ensure everything works
3. **Run deployment script** again:
   ```powershell
   cd backend
   .\deploy_to_hf.ps1
   ```
4. **Wait for rebuild** (5-10 minutes)
5. **Verify changes** via `/docs` or API tests

---

## 📝 Important Notes

### Data Persistence
- ⚠️ Spaces are **ephemeral** - files in `outputs/` are lost on restart
- Use external storage for permanent files
- Videos are regenerated on demand

### Model Files
- Must be included in deployment
- Located in `pretrained/` directory
- Size limits apply (check HF Spaces limits)

### Environment Variables
- Set in Space settings, not in code
- Never commit API keys to git
- Use Secrets for sensitive data

### Rate Limits
- OpenAI API has rate limits
- Consider implementing caching
- Monitor usage to avoid overages

---

## ✅ Deployment Checklist

Before going live:

- [ ] Backend deployed to HF Spaces
- [ ] OPENAI_API_KEY set in Space settings
- [ ] Space is running (green status)
- [ ] `/health` endpoint returns OK
- [ ] `/docs` page accessible
- [ ] Test inference endpoints work
- [ ] Frontend API_BASE_URL updated
- [ ] Chrome extension backendUrl updated
- [ ] CORS working (test from frontend)
- [ ] WebSocket connections working
- [ ] Model files loading correctly

---

## 🎉 Success!

Your backend is now deployed at:
**https://lamaq-signlink-hackx.hf.space**

Next steps:
1. Deploy frontend to Vercel
2. Update Chrome extension
3. Test all features end-to-end
4. Share with users!

---

## 🆘 Need Help?

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Space Settings**: https://huggingface.co/spaces/Lamaq/signlink-hackx/settings
