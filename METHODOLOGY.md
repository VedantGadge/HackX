# 🎯 SignLink Implementation Methodology

## 1. Problem Statement
Bridge communication gap between hearing and deaf communities through real-time AI-powered ASL translation.

## 2. System Architecture

### Multi-Tier Architecture:
```
User Interface (Frontend/Extension)
         ↓
REST API + WebSocket (Backend)
         ↓
ML Pipeline (MediaPipe + Scikit-learn)
         ↓
LLM Integration (OpenAI GPT-4o-mini)
         ↓
Video Database (WLASL Dataset)
```

## 3. Core Implementation Phases

### Phase 1: Gesture Recognition (ASL → Text)
**Method**: Computer Vision + Machine Learning
1. **Hand Detection**: MediaPipe Hands detects 21 landmarks per hand
2. **Feature Extraction**: Extract 63 features (21 points × 3 coordinates: x, y, z)
3. **Classification**: Scikit-learn SVC with RBF kernel
4. **Models**: 
   - `gesture_model.pkl` - 30+ ASL gestures
   - `letter_model.pkl` - A-Z fingerspelling

**Pipeline**:
```
Webcam → MediaPipe → Hand Landmarks → Normalization → SVC Model → Predicted Sign
```

### Phase 2: Text → ASL Video Generation
**Method**: NLP + Video Composition
1. **Text Input**: User provides English sentence
2. **Gloss Conversion**: OpenAI GPT-4o-mini converts English → ASL gloss format
   - Example: "I love you" → "I LOVE YOU"
3. **Token Matching**: Map gloss tokens to WLASL video database (2000+ signs)
4. **Video Composition**: Concatenate individual sign videos using OpenCV
5. **Output**: MP4 video file served via FastAPI

**Pipeline**:
```
English Text → GPT-4o-mini → ASL Gloss → WLASL Mapper → Video URLs → Download → Compose → Output Video
```

### Phase 3: Real-Time Classroom Feature
**Method**: WebSocket Communication + Audio Transcription
1. **Teacher Side**: Records audio lecture
2. **Transcription**: OpenAI Whisper converts speech → text
3. **Translation**: Text → ASL video (reuses Phase 2)
4. **Broadcasting**: WebSocket streams to all connected students
5. **Student Side**: Real-time video playback

**Pipeline**:
```
Teacher Audio → Whisper API → Text → Gloss → Video → WebSocket → Student Display
```

### Phase 4: Chrome Extension Integration
**Method**: Content Script Injection
1. **Caption Detection**: Intercept YouTube closed captions
2. **Tokenization**: Send text to backend `/tokenize-text` API
3. **Video Fetching**: Request ASL videos for each token
4. **Overlay Display**: Inject video player into YouTube UI

## 4. Technology Stack Implementation

### Backend (FastAPI):
```python
# Core inference endpoint
@app.post("/infer-frame")
async def infer_frame(frame: UploadFile):
    # 1. Load image
    image = cv.imdecode(np_arr, cv.IMREAD_COLOR)
    
    # 2. MediaPipe hand detection
    results = hands.process(image_rgb)
    
    # 3. Extract landmarks
    landmarks = [lm.x, lm.y, lm.z for lm in hand_landmarks]
    
    # 4. Normalize features
    normalized = (landmarks - mean) / std
    
    # 5. Predict using SVC model
    prediction = model.predict([normalized])
    
    return {"gesture": prediction, "confidence": confidence}
```

### Frontend (JavaScript):
```javascript
// Capture webcam frame every 100ms
setInterval(() => {
    canvas.getContext('2d').drawImage(video, 0, 0);
    canvas.toBlob(blob => {
        // Send to backend
        fetch(`${API_BASE_URL}/infer-frame`, {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => displayResult(data.gesture));
    });
}, 100);
```

## 5. Machine Learning Pipeline

### Training Process (Offline):
1. **Data Collection**: ASL gesture videos/images with labels
2. **Preprocessing**: MediaPipe landmark extraction
3. **Feature Engineering**: Normalize coordinates, calculate distances/angles
4. **Model Training**: Scikit-learn SVC with grid search
5. **Validation**: 80/20 train-test split, cross-validation
6. **Export**: Joblib serialization → `.pkl` files

### Inference Process (Real-time):
```python
# Load model once at startup
model = joblib.load('pretrained/gesture_model.pkl')

# Per-frame inference
def run_inference_on_frame(frame):
    landmarks = extract_mediapipe_landmarks(frame)
    features = normalize_features(landmarks)
    prediction = model.predict([features])
    confidence = model.predict_proba([features]).max()
    return prediction, confidence
```

## 6. LLM Integration Methodology

### Text-to-Gloss Conversion:
```python
def text_to_gloss(text: str) -> str:
    prompt = f"""Convert this English sentence to ASL gloss format:
    English: {text}
    ASL Gloss: """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

### Why LLM?
- ASL has different grammar than English
- Word order changes: "I am going home" → "HOME I GO"
- GPT-4o-mini handles linguistic nuances

## 7. Video Composition Algorithm

```python
def compose_video_from_gloss(gloss_tokens: list) -> str:
    clips = []
    
    for token in gloss_tokens:
        # 1. Find video URL from WLASL
        video_url = wlasl_fetcher.get_video_url(token)
        
        # 2. Download video
        video_path = download_video(video_url, cache_dir='/tmp')
        
        # 3. Load with OpenCV
        clips.append(video_path)
    
    # 4. Concatenate clips
    output_path = concatenate_videos(clips, output='/tmp/output.mp4')
    
    return output_path
```

## 8. WebSocket Communication Pattern

```python
# Backend (FastAPI)
class ConnectionManager:
    def __init__(self):
        self.connections = {}
    
    async def broadcast(self, room_id: str, message: dict):
        for connection in self.connections[room_id]:
            await connection.send_json(message)

@app.websocket("/ws/classroom/{room_id}/teacher")
async def teacher_websocket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    while True:
        audio_data = await websocket.receive_bytes()
        text = transcribe_audio(audio_data)  # Whisper API
        video_url = generate_asl_video(text)
        await manager.broadcast(room_id, {"video_url": video_url})
```

```javascript
// Frontend (JavaScript)
const socket = new WebSocket(`ws://localhost:8000/ws/classroom/${roomId}/student`);

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    videoPlayer.src = data.video_url;
    videoPlayer.play();
};
```

## 9. Deployment Strategy

### Containerization (Docker):
```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN apt-get install libgl1  # OpenCV dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Ephemeral Storage Pattern:
- Use `/tmp` for generated files (HF Spaces requirement)
- Cache WLASL videos on-demand
- No persistent storage needed

## 10. Performance Optimizations

### 1. Model Loading:
- Load models once at startup (not per request)
- Keep in memory for fast inference

### 2. Video Caching:
- Download WLASL videos to `/tmp` on first request
- Subsequent requests use cache (until restart)

### 3. Async Operations:
- FastAPI async endpoints for concurrent requests
- Non-blocking WebSocket connections

### 4. Feature Extraction:
- MediaPipe runs on CPU efficiently (~50ms per frame)
- Batch processing for multiple frames

## 11. Error Handling & Fallbacks

```python
def get_video_for_token(token: str):
    try:
        # Try local cache first
        if exists(f'/tmp/videos/{token}.mp4'):
            return serve_cached_video(token)
        
        # Try WLASL database
        video_url = wlasl_fetcher.get_video(token)
        return download_and_serve(video_url)
        
    except Exception as e:
        logger.warning(f"Video not found for {token}")
        return None  # Frontend displays "No video available"
```

## 12. Key Innovations

1. **Hybrid Approach**: Combines CV (MediaPipe) + ML (SVC) + LLM (GPT)
2. **Real-time Processing**: <100ms latency for gesture recognition
3. **Dynamic Video Generation**: On-demand composition from database
4. **Multi-Modal**: Supports gesture input, text input, audio input
5. **Extensible**: Chrome extension for YouTube integration

## 13. Evaluation Metrics

- **Gesture Recognition Accuracy**: ~85-90% (depends on lighting, hand position)
- **Inference Speed**: 50ms per frame (20 FPS)
- **Video Generation**: 2-5 seconds for 3-word sentence
- **WebSocket Latency**: <500ms teacher-to-student
- **API Response Time**: <100ms for health checks, 1-3s for transcription

---

**Implementation Timeline**: 4 weeks
**Team Size**: 1 developer + AI assistants
**Lines of Code**: ~3000 (Backend: 1500, Frontend: 1000, Extension: 500)
