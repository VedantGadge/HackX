---
title: SignLink
emoji: 🤟
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
---

# 🤟 SignLink - AI Sign Language Translator

Real-time AI-powered American Sign Language (ASL) translator with gesture recognition, video generation, and classroom features.

## 🌟 Features

- **Real-time Gesture Recognition**: Detect ASL gestures and fingerspelling letters using ML models
- **Video Translation**: Convert English text to ASL sign language videos
- **Classroom Mode**: Live teacher-student WebSocket communication with real-time transcription
- **Chrome Extension Support**: YouTube caption translation to ASL
- **LLM Integration**: Smart text-to-gloss conversion using OpenAI GPT

## 🚀 API Endpoints

### Core Inference
- `POST /infer-frame` - Gesture detection from image frame
- `POST /infer-letter` - Fingerspelling letter detection
- `GET /model-status` - Check ML model status
- `GET /health` - Health check endpoint

### Video Translation
- `POST /reverse-translate-video` - Generate full ASL video from text
- `POST /process-confirmed-words` - Convert gloss tokens to English

### Chrome Extension
- `POST /tokenize-text` - Tokenize text for ASL translation
- `GET /token-video/{token}` - Get video clip for specific sign

### Classroom (WebSocket)
- `WS /ws/classroom/{room_id}/teacher` - Teacher dashboard connection
- `WS /ws/classroom/{room_id}/student` - Student view connection

## 📚 Documentation

Visit `/docs` for interactive API documentation (Swagger UI).

## 🔧 Environment Variables

**Required:**
- `OPENAI_API_KEY` - OpenAI API key for transcription and LLM features

⚠️ **Important**: Set this in Space Settings → Variables and secrets

## 🎯 Usage

### Test the API
```bash
curl https://lamaq-signlink-hackx.hf.space/health
```

### Real-time Inference
```bash
curl -X POST https://lamaq-signlink-hackx.hf.space/infer-frame \
  -F "frame=@image.jpg"
```

### Generate ASL Video
```bash
curl -X POST https://lamaq-signlink-hackx.hf.space/reverse-translate-video \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

## 🌐 Frontend Integration

Update your frontend's `API_BASE_URL` to:
```javascript
window.API_BASE_URL = 'https://lamaq-signlink-hackx.hf.space';
```

## 🧩 Chrome Extension

Update the `backendUrl` in `content.js`:
```javascript
let backendUrl = 'https://lamaq-signlink-hackx.hf.space';
```

## 📦 Tech Stack

- **Framework**: FastAPI
- **ML**: MediaPipe, scikit-learn, PyTorch
- **Computer Vision**: OpenCV
- **LLM**: OpenAI GPT-4o-mini
- **Speech**: OpenAI Whisper
- **Video**: WLASL dataset (2000+ signs)

## � Storage

**Ephemeral Storage**: This Space uses `/tmp` for temporary file storage. Generated videos and outputs are cached in memory during runtime but **will be lost on Space restart**. This is standard for HF Spaces.

## �🔒 CORS

CORS is enabled for all origins to support frontend and extension connections.

## 📝 License

Apache-2.0