# Backend API Documentation

## 🎯 API-Only Backend for Hugging Face Deployment

This backend is designed to be deployed independently on Hugging Face Spaces, with the frontend hosted separately on Vercel.

## 🌐 Base URL

**Local Development:** `http://localhost:8000`
**Production (HF Spaces):** `https://your-space-name.hf.space`

---

## 📋 Core API Endpoints

### 1. Health & Status

#### `GET /health`
Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

#### `GET /model-status`
Get detailed model information.

**Response:**
```json
{
  "ml_libraries_available": true,
  "gesture_model_loaded": true,
  "letter_model_loaded": true,
  "model_type": ".pkl",
  "gesture_classes": ["hello", "thanks", "please"],
  "letter_classes": ["A", "B", "C"],
  "gesture_actions_count": 3,
  "letter_actions_count": 26,
  "demo_mode": false
}
```

#### `GET /`
API information and endpoint list.

**Response:**
```json
{
  "name": "Sign Language Translator API",
  "version": "2.0.0",
  "status": "running",
  "documentation": "/docs",
  "endpoints": { ... }
}
```

---

## 🤖 Inference Endpoints

### 2. Gesture Inference

#### `POST /infer-frame`
Detect sign language gesture from an image frame.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `frame` (file): JPEG or PNG image
  - `return_annotated` (boolean, optional): Return annotated image with landmarks

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('frame', imageBlob, 'frame.jpg');
formData.append('return_annotated', 'true');

const response = await fetch('http://localhost:8000/infer-frame', {
  method: 'POST',
  body: formData
});

const data = await response.json();
```

**Response:**
```json
{
  "detected_sign": "hello",
  "confidence": 0.92,
  "detections": [
    {
      "class": "hello",
      "confidence": 0.92
    }
  ],
  "timing": {
    "decode": 0.005,
    "inference": 0.045,
    "total": 0.050
  },
  "annotated_frame": "data:image/jpeg;base64,..." // if return_annotated=true
}
```

### 3. Letter Inference

#### `POST /infer-letter`
Detect ASL fingerspelling letter from an image frame.

**Request:**
- Same format as `/infer-frame`

**Response:**
```json
{
  "detected_letter": "A",
  "confidence": 0.95,
  "detections": [
    {
      "class": "A",
      "confidence": 0.95
    }
  ],
  "timing": { ... }
}
```

---

## 🎬 Video Translation Endpoints

### 4. Reverse Translation (Text to Sign Video)

#### `POST /reverse-translate-video`
Convert text to sign language video.

**Request:**
```json
{
  "text": "Hello world",
  "glossTokens": ["hello", "world"]  // optional, will use LLM if not provided
}
```

**Response:**
```json
{
  "video_url": "/outputs/reverse_20251031_120345_000000.mp4",
  "file": "reverse_20251031_120345_000000.mp4",
  "meta": {
    "fps": 25.0,
    "width": 640,
    "height": 480,
    "frames": 150,
    "missing": [],
    "codec": "avc1"
  },
  "tokens": ["hello", "world"]
}
```

**Usage in Frontend:**
```javascript
const response = await fetch('http://localhost:8000/reverse-translate-video', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: "Hello world" })
});

const data = await response.json();
const videoUrl = `http://localhost:8000${data.video_url}`;
// Play video in <video> element
```

### 5. Process Confirmed Words (Gloss to English)

#### `POST /process-confirmed-words`
Convert sign language gloss tokens to natural English using LLM.

**Request:**
```json
{
  "confirmedWords": ["me", "go", "school"]
}
```

**Response:**
```json
{
  "sentence": "I am going to school"
}
```

---

## 📁 File Serving

### 6. Get Generated Video

#### `GET /outputs/{filename}`
Retrieve generated sign language videos.

**Example:**
```
GET /outputs/reverse_20251031_120345_000000.mp4
```

**Features:**
- Supports HTTP Range requests (for video seeking)
- Returns 206 Partial Content for range requests
- Returns 404 if file not found

---

## 🏫 Classroom WebSocket Endpoints

### 7. Teacher WebSocket

#### `WS /ws/classroom/{room_id}/teacher`
WebSocket connection for teachers.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/classroom/ABC123/teacher');

ws.onopen = () => {
  console.log('Teacher connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

**Send Message:**
```javascript
ws.send(JSON.stringify({
  type: 'send_speech',
  audio: base64AudioData
}));
```

**Received Messages:**
```json
{
  "type": "teacher_connected",
  "room_id": "ABC123",
  "message": "Connected. Waiting for students..."
}

{
  "type": "caption_received",
  "text": "Hello students",
  "timestamp": "2025-10-31T12:00:00",
  "tokens": ["hello", "students"]
}

{
  "type": "error",
  "message": "Error description"
}
```

### 8. Student WebSocket

#### `WS /ws/classroom/{room_id}/student`
WebSocket connection for students.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/classroom/ABC123/student');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'video_broadcast') {
    // Play video
    videoElement.src = `http://localhost:8000${data.video_url}`;
    videoElement.play();
  }
};
```

**Received Messages:**
```json
{
  "type": "student_connected",
  "room_id": "ABC123",
  "message": "Connected to classroom"
}

{
  "type": "video_broadcast",
  "video_url": "/outputs/seg_abc123.mp4",
  "duration": 3.5,
  "tokens": ["hello", "world"],
  "text": "Hello world"
}
```

---

## 🔧 CORS Configuration

All endpoints support CORS with:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: *`
- `Access-Control-Allow-Headers: *`

Perfect for frontend hosted on Vercel!

---

## 🚀 Deployment on Hugging Face Spaces

### Step 1: Create Space
1. Go to https://huggingface.co/spaces
2. Create new Space
3. Choose **Docker** as SDK

### Step 2: Configure Space
Set these in Space settings:
- **Space SDK:** Docker
- **Port:** 8000
- **Environment Variables:**
  - `OPENAI_API_KEY`: Your OpenAI API key

### Step 3: Deploy
```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy backend files
cp -r /path/to/backend/* .

# Commit and push
git add .
git commit -m "Deploy backend API"
git push
```

### Step 4: Get API URL
Your API will be available at:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

---

## 🌐 Frontend Integration (Vercel)

### Environment Variables in Vercel

Set this in your Vercel project:
```
NEXT_PUBLIC_API_URL=https://your-space-name.hf.space
```

### Example API Calls from Frontend

**Gesture Detection:**
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function detectGesture(imageBlob) {
  const formData = new FormData();
  formData.append('frame', imageBlob);
  
  const response = await fetch(`${API_URL}/infer-frame`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

**Video Translation:**
```javascript
async function translateToVideo(text) {
  const response = await fetch(`${API_URL}/reverse-translate-video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  
  const data = await response.json();
  return `${API_URL}${data.video_url}`;
}
```

**WebSocket Connection:**
```javascript
const ws = new WebSocket(`wss://your-space-name.hf.space/ws/classroom/${roomId}/student`);
```

---

## 📊 Rate Limits

Hugging Face Spaces free tier:
- No hard rate limits
- CPU-based inference
- Auto-sleep after inactivity

For production, consider:
- Caching responses
- Implementing request queuing
- Using Hugging Face Pro for GPU

---

## 🔒 Security Notes

1. **API Keys:** Always use environment variables
2. **CORS:** Currently allows all origins - restrict in production
3. **File Upload:** Limited to image files only
4. **WebSocket:** No authentication - add JWT tokens for production

---

## 🧪 Testing

**Local Testing:**
```bash
# Start backend
cd backend
python start.py

# Test health
curl http://localhost:8000/health

# Test inference (with image file)
curl -X POST -F "frame=@test.jpg" http://localhost:8000/infer-frame
```

**Production Testing:**
```bash
# Test deployed API
curl https://your-space-name.hf.space/health

# Test from frontend
fetch('https://your-space-name.hf.space/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 📚 Interactive API Documentation

Once deployed, visit:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

Both provide interactive API testing!

---

## 💡 Best Practices

1. **Always check health endpoint** before making requests
2. **Handle 503 errors** (model not loaded)
3. **Implement retry logic** for transient failures
4. **Cache video results** (deterministic output for same text)
5. **Use WebSocket reconnection** for classroom feature
6. **Compress images** before sending (smaller = faster)

---

**Need help?** Check `/docs` for interactive API testing!
