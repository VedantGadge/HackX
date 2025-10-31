# Sign Language Translator - Refactored Architecture

A full-stack sign language translation system with real-time gesture detection, video composition, and classroom features. Refactored from Flask to FastAPI with containerized deployment.

## 🏗️ Architecture

```
├── frontend/              # Frontend assets
│   ├── templates/        # HTML templates (Jinja2)
│   ├── static/          # CSS, JS, images
│   └── chrome_extension/ # Browser extension
├── backend/              # FastAPI backend
│   ├── app/             # Main application
│   │   └── main.py      # FastAPI app
│   ├── models/          # ML models
│   ├── services/        # Business logic
│   │   ├── revtrans.py  # LLM translation
│   │   └── dynamic_video_fetcher.py
│   ├── utils/           # Utilities
│   ├── pretrained/      # Model weights
│   ├── mapper/          # WLASL JSON data
│   ├── videos/          # Video clips
│   └── outputs/         # Generated videos
└── deployment/          # Docker deployment
    ├── docker-compose.yml
    └── nginx.conf
```

## ✨ Features

- **Real-time Gesture Detection**: MediaPipe + scikit-learn
- **Letter Recognition**: ASL fingerspelling
- **Video Composition**: WLASL dataset integration (2000+ signs)
- **LLM Translation**: OpenAI GPT for gloss-to-English
- **Classroom Mode**: Teacher-student WebSocket communication
- **Chrome Extension**: Browser integration
- **RESTful API**: FastAPI with automatic docs
- **WebSocket Support**: Real-time communication

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (for containerized deployment)
- OpenAI API Key (for transcription/LLM features)

### Local Development

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_key_here"

# Run the backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup

The frontend is served by the FastAPI backend. Access it at:
- Main App: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Classroom: http://localhost:8000/classroom

### Docker Deployment

#### 1. Setup Environment

```bash
cd deployment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

#### 2. Build and Run

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### 3. Access

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📋 API Endpoints

### Core Endpoints

- `GET /` - Main application
- `GET /health` - Health check
- `GET /model-status` - Model status
- `GET /classroom` - Classroom homepage
- `GET /teacher` - Teacher dashboard
- `GET /student?room_id=ABC` - Student dashboard

### Inference Endpoints

- `POST /infer-frame` - Gesture detection from image
- `POST /infer-letter` - Letter recognition from image
- `POST /reverse-translate-video` - Generate sign video from text
- `POST /process-confirmed-words` - Convert gloss to English

### WebSocket Endpoints

- `WS /ws/classroom/{room_id}/teacher` - Teacher WebSocket
- `WS /ws/classroom/{room_id}/student` - Student WebSocket

Full API documentation available at `/docs` when running.

## 🧪 Testing

### Test Backend Locally

```bash
cd backend

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/model-status

# Test inference (requires image file)
curl -X POST -F "frame=@test_image.jpg" http://localhost:8000/infer-frame
```

### Test Docker Container

```bash
cd deployment

# Build and test
docker-compose up -d
docker-compose ps  # Check status
docker-compose logs backend  # View logs

# Test health
curl http://localhost:8000/health

# Stop
docker-compose down
```

## 🎓 Classroom Feature

### For Teachers

1. Navigate to `/teacher`
2. Share room ID with students
3. Speak into microphone
4. System transcribes → converts to gloss → generates sign video
5. Video broadcasts to all students in real-time

### For Students

1. Navigate to `/student?room_id=ABC123`
2. Receive and view sign language videos from teacher
3. Real-time synchronization

## 📦 Model Files

Place these files in `backend/pretrained/`:
- `gesture_model.pkl` - Gesture recognition model
- `letter_model.pkl` - Letter recognition model

Place WLASL JSON in `backend/mapper/`:
- `WLASL_v0.3.json` - WLASL video mapper (2000+ signs)

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY` - OpenAI API key (required for LLM features)
- `BACKEND_PORT` - Backend port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 80)

### Customization

- Modify `backend/app/main.py` for API changes
- Update `frontend/static/` for UI changes
- Edit `deployment/nginx.conf` for routing

## 🚢 Hugging Face Spaces Deployment

### Optimized for Ephemeral Deployment

The backend is containerized with:
- Lightweight Python 3.10-slim base
- Minimal system dependencies
- No heavy pre-installed libraries
- Fast startup time

### Deploy to Hugging Face

1. Push backend code to Hugging Face Space
2. Set environment variables in Space settings
3. Use Dockerfile for automatic deployment
4. Space will handle container orchestration

```python
# In Hugging Face Space, add:
# - secrets: OPENAI_API_KEY
# - runtime: Docker
# - dockerfile: backend/Dockerfile
```

## 📊 Performance

- **Startup Time**: ~5-10 seconds
- **Inference Time**: ~50-100ms per frame
- **Video Generation**: ~2-5 seconds (depends on gloss length)
- **WebSocket Latency**: <100ms

## 🐛 Troubleshooting

### Model Not Loading

- Ensure `.pkl` files are in `backend/pretrained/`
- Check file permissions
- Verify Python version compatibility

### WebSocket Connection Issues

- Check CORS settings
- Verify room_id is valid
- Check browser console for errors

### Video Playback Issues

- Ensure H.264 codec support
- Check browser compatibility
- Verify output directory permissions

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributors

Original Flask version converted to FastAPI architecture

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WLASL Dataset](https://github.com/dxli94/WLASL)
- [MediaPipe Documentation](https://google.github.io/mediapipe/)
- [OpenAI API](https://platform.openai.com/docs)
