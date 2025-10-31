"""
FastAPI Backend for Sign Language Translator
Converted from Flask to FastAPI with WebSocket support
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional, List, Dict
import hashlib
import shutil
import os
import tempfile
import logging
import io
import time
import traceback
import json
import secrets
import base64
import sys
import subprocess

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ML / CV deps
import numpy as np
import cv2 as cv
import torch
import joblib
import mediapipe as mp
import math
import difflib

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
try:
    from utils.setup import get_classes, get_colors
    from utils.boxes import rescale_bboxes
except Exception:
    def get_classes():
        return ["class_0", "class_1", "class_2"]
    def get_colors():
        return [(0,255,0), (255,0,0), (0,0,255)]
    def rescale_bboxes(bboxes, size_hw):
        H, W = size_hw
        b = bboxes.detach().cpu().numpy()
        if b.shape[-1] == 4:
            return torch.tensor(b)
        return torch.tensor(b)

print("✅ ML dependencies loaded successfully")

# Initialize FastAPI app
app = FastAPI(title="Sign Language Translator API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")

# Optional: Only mount templates if frontend folder exists (for local dev)
# For production deployment, frontend will be on Vercel
if os.path.exists(FRONTEND_DIR):
    templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))
    if os.path.exists(os.path.join(FRONTEND_DIR, "static")):
        app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
    logger.info(f"✅ Frontend assets found at: {FRONTEND_DIR}")
else:
    templates = None
    logger.warning("⚠️ Frontend folder not found - running in API-only mode")

# Configuration
ALLOWED_IMAGE_MIME = {"image/jpeg", "image/png"}
CONFIDENCE_THRESHOLD = 0.8

# Output directory for generated artifacts
# Use /tmp for HF Spaces ephemeral storage (files are lost on restart)
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'signlink_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)
logger.info(f"📁 Using temporary output directory: {OUTPUT_DIR}")

# In-memory cache and storage
_REVERSE_SEGMENT_CACHE: Dict[str, str] = {}
active_classrooms: Dict[str, Dict] = {}

# WebSocket connection manager for classroom feature
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.teacher_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, is_teacher: bool = False):
        await websocket.accept()
        if is_teacher:
            self.teacher_connections[room_id] = websocket
            if room_id not in active_classrooms:
                active_classrooms[room_id] = {'teacher': websocket, 'students': []}
            else:
                active_classrooms[room_id]['teacher'] = websocket
        else:
            if room_id not in self.active_connections:
                self.active_connections[room_id] = []
            self.active_connections[room_id].append(websocket)
            if room_id not in active_classrooms:
                active_classrooms[room_id] = {'teacher': None, 'students': [websocket]}
            else:
                active_classrooms[room_id]['students'].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections and websocket in self.active_connections[room_id]:
            self.active_connections[room_id].remove(websocket)
        if room_id in active_classrooms and websocket in active_classrooms[room_id].get('students', []):
            active_classrooms[room_id]['students'].remove(websocket)
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# Token normalization helpers
def _stem_token(w: str) -> str:
    w = w.lower().strip()
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w

def _map_tokens_to_available(tokens: list, available: list):
    """Map tokens to available videos with stemming and synonyms"""
    avail = set([a.lower() for a in available])
    mapped = []
    missing = []

    SYN = {
        'those': 'they', 'these': 'they', 'them': 'they', 'people': 'they',
        'achieve': 'success', 'achievement': 'success',
        'great': 'good', 'nice': 'good',
        'things': 'thing', 'stuff': 'thing',
        'life': 'live', 'today': 'day', 'exam': 'test',
    }

    for t in tokens:
        t0 = (t or '').lower().strip()
        if not t0:
            continue
        if t0 in avail:
            mapped.append(t0)
            continue
        t1 = _stem_token(t0)
        if t1 in avail:
            mapped.append(t1)
            continue
        t2 = SYN.get(t0)
        if t2 and t2 in avail:
            mapped.append(t2)
            continue
        close = difflib.get_close_matches(t0, list(avail), n=1, cutoff=0.86)
        if close:
            mapped.append(close[0])
            continue
        missing.append(t0)
    return mapped, missing

# Model Loading
MODEL_FILE = os.path.join(BACKEND_DIR, "pretrained", "gesture_model.pkl")
try:
    model = joblib.load(MODEL_FILE)
    logger.info("✅ PKL Model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load PKL model: {e}")
    model = None

# Letter Model Loading
LETTER_MODEL_FILE = os.path.join(BACKEND_DIR, "pretrained", "letter_model.pkl")
try:
    letter_model = joblib.load(LETTER_MODEL_FILE)
    logger.info("✅ Letter PKL Model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load Letter PKL model: {e}")
    letter_model = None

# Landmark normalization utilities
def normalize_landmarks(landmarks):
    """Normalize landmarks like during training"""
    wrist = landmarks[0]
    translated = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]
    scale = math.sqrt(translated[9][0]**2 + translated[9][1]**2 + translated[9][2]**2)
    if scale < 1e-6:
        scale = 1.0
    normalized = [(x/scale, y/scale, z/scale) for (x, y, z) in translated]
    return [coord for triple in normalized for coord in triple]

def empty_hand():
    return [0.0] * (21 * 3)

# Inference functions
def run_inference_on_frame(frame_bgr: np.ndarray):
    """Run model inference on a single BGR frame"""
    global model
    if model is None:
        raise RuntimeError("Model not loaded")

    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    try:
        rgb_frame = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        annotated_frame = frame_bgr.copy()

        left_hand, right_hand = None, None

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                score = handedness.classification[0].score

                if score < 0.7:
                    continue

                mp_drawing.draw_landmarks(
                    annotated_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )

                norm = normalize_landmarks(hand_landmarks.landmark)

                if label == "Left":
                    left_hand = norm
                else:
                    right_hand = norm

        if left_hand is None:
            left_hand = empty_hand()
        if right_hand is None:
            right_hand = empty_hand()

        features = np.array([left_hand + right_hand])

        if any(v != 0.0 for v in features[0]):
            pred = model.predict(features)[0]

            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features).max()
                confidence = float(proba)
                text = f"Gesture: {pred} ({confidence:.2f})"
            else:
                confidence = 1.0
                text = f"Gesture: {pred}"

            cv.putText(annotated_frame, text, (10, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            return {
                "detected_sign": pred,
                "confidence": confidence,
                "detections": [{"class": pred, "confidence": confidence}],
                "annotated_frame": annotated_frame
            }
        else:
            return {
                "detected_sign": None,
                "confidence": 0.0,
                "detections": [],
                "annotated_frame": annotated_frame
            }
    finally:
        hands.close()

def run_letter_inference_on_frame(frame_bgr: np.ndarray):
    """Run letter model inference on a single BGR frame"""
    global letter_model
    if letter_model is None:
        raise RuntimeError("Letter model not loaded")

    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    try:
        rgb_frame = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        annotated_frame = frame_bgr.copy()

        if results.multi_hand_landmarks and results.multi_handedness:
            hand_landmarks = results.multi_hand_landmarks[0]
            handedness = results.multi_handedness[0]
            
            if handedness.classification[0].score >= 0.7:
                mp_drawing.draw_landmarks(
                    annotated_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
                )

                norm = normalize_landmarks(hand_landmarks.landmark)
                features = np.array([norm])
                pred = letter_model.predict(features)[0]

                if hasattr(letter_model, "predict_proba"):
                    proba = letter_model.predict_proba(features).max()
                    confidence = float(proba)
                    text = f"Letter: {pred} ({confidence:.2f})"
                else:
                    confidence = 1.0
                    text = f"Letter: {pred}"

                cv.putText(annotated_frame, text, (10, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                return {
                    "detected_letter": pred,
                    "confidence": confidence,
                    "detections": [{"class": pred, "confidence": confidence}],
                    "annotated_frame": annotated_frame
                }

        return {
            "detected_letter": None,
            "confidence": 0.0,
            "detections": [],
            "annotated_frame": annotated_frame
        }
    finally:
        hands.close()

# Video composition helpers
def _list_available_video_tokens() -> List[str]:
    """Return available token basenames from WLASL mapper and local videos directory"""
    tokens = set()
    
    try:
        from services.dynamic_video_fetcher import WLASLVideoFetcher
        fetcher = WLASLVideoFetcher()
        wlasl_glosses = list(fetcher.gloss_index.keys())
        tokens.update(wlasl_glosses)
        logger.info(f"✅ Loaded {len(wlasl_glosses)} glosses from WLASL mapper")
    except Exception as e:
        logger.warning(f"⚠️ Could not load WLASL glosses: {e}")
    
    base_vid_dir = os.path.join(BACKEND_DIR, 'videos')
    if os.path.isdir(base_vid_dir):
        for name in os.listdir(base_vid_dir):
            if name.lower().endswith('.mp4'):
                tokens.add(os.path.splitext(name)[0].lower())
    
    return sorted(tokens)

def _text_to_gloss_tokens(text: str) -> List[str]:
    """Convert a free-form sentence into a list of gloss-like tokens"""
    if not text:
        return []
    import re

    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9'\s]", " ", s)
    words = [w for w in re.split(r"\s+", s) if w]

    contr = {
        "i'm": "i", "im": "i", "we're": "we", "you're": "you", "they're": "they",
        "can't": "cannot", "won't": "will", "don't": "do", "doesn't": "do", "didn't": "do",
    }
    words = [contr.get(w, w) for w in words]

    def stem(w: str) -> str:
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > 3 and w.endswith(suf):
                return w[: -len(suf)]
        return w

    stop = {"the", "a", "an", "is", "am", "are", "to", "at", "in", "on", "for", "of", "and", "or", "with", "be", "was", "were", "will", "would", "should", "could", "have", "has", "had", "do", "did", "does", "that", "this", "these", "those", "it"}
    candidates = [stem(w) for w in words if w not in stop]

    avail = set(_list_available_video_tokens())
    filtered = [w for w in candidates if w in avail]
    return filtered or candidates

def compose_video_from_gloss(gloss_tokens):
    """Concatenate per-token mp4 clips into a single mp4 in outputs"""
    try:
        from services.dynamic_video_fetcher import WLASLVideoFetcher
        fetcher = WLASLVideoFetcher()
        logger.info("✅ Using WLASL fetcher to load videos")
    except Exception as e:
        logger.warning(f"⚠️ WLASL fetcher unavailable: {e}")
        fetcher = None
    
    files = []
    missing = []
    
    for t in gloss_tokens:
        name = str(t).strip().lower()
        if not name:
            continue
        
        try:
            if fetcher:
                videos = fetcher.get_video_paths_for_gloss(name, source="aslbrick", max_videos=1)
                if videos:
                    files.extend(videos)
                else:
                    raise Exception("No WLASL video found")
            else:
                raise Exception("Fetcher not available")
        except Exception:
            base_vid_dir = os.path.join(BACKEND_DIR, 'videos')
            cand = os.path.join(base_vid_dir, f"{name}.mp4")
            if os.path.exists(cand):
                files.append(cand)
            else:
                missing.append(name)

    if not files:
        available_tokens = _list_available_video_tokens()
        raise FileNotFoundError(f"No matching video clips found for tokens: {gloss_tokens}")

    # Use FFmpeg for concatenation instead of OpenCV VideoWriter
    out_name = f"reverse_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.mp4"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    
    # Create concat file for FFmpeg
    concat_file = os.path.join(OUTPUT_DIR, f"concat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.txt")
    with open(concat_file, 'w') as f:
        for video_path in files:
            # Escape single quotes and use absolute paths
            escaped_path = video_path.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
    
    try:
        logger.info(f"🎬 Concatenating {len(files)} videos using FFmpeg...")
        
        # Use FFmpeg to concatenate videos directly
        result = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c", "copy",  # Copy codec (no re-encoding)
            out_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ FFmpeg concatenation error: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed to concatenate videos: {result.stderr}")
        
        logger.info(f"✅ Video composed successfully: {out_name}")
        
        # Get video metadata
        first = cv.VideoCapture(out_path)
        fps = first.get(cv.CAP_PROP_FPS) or 25.0
        width = int(first.get(cv.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(first.get(cv.CAP_PROP_FRAME_HEIGHT) or 480)
        total_frames = int(first.get(cv.CAP_PROP_FRAME_COUNT) or 0)
        first.release()
        
    finally:
        # Clean up concat file
        if os.path.exists(concat_file):
            os.remove(concat_file)
            logger.debug(f"🧹 Cleaned up concat file: {concat_file}")

    meta = {'fps': fps, 'width': width, 'height': height, 'frames': total_frames, 'missing': missing, 'method': 'ffmpeg_concat'}
    return out_name, meta

# Helper for transcription
def transcribe_audio(audio_base64: str) -> str:
    """Convert base64-encoded audio data to text using OpenAI Whisper API"""
    try:
        logger.info("🎤 Transcribing audio via OpenAI Whisper...")
        audio_bytes = base64.b64decode(audio_base64)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"
        
        # Check if API key is set
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        import openai
        
        # Use legacy API for openai==1.3.5
        openai.api_key = api_key
        
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        
        text = transcript.get('text', '').strip()
        logger.info(f"✅ Transcription complete: '{text}'")
        return text
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        logger.error(traceback.format_exc())
        raise

# ==================== HTTP ROUTES ====================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Sign Language Translator API",
        "version": "2.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "inference": {
                "gesture": "POST /infer-frame",
                "letter": "POST /infer-letter"
            },
            "translation": {
                "reverse_video": "POST /reverse-translate-video",
                "process_words": "POST /process-confirmed-words"
            },
            "classroom": {
                "teacher_ws": "WS /ws/classroom/{room_id}/teacher",
                "student_ws": "WS /ws/classroom/{room_id}/student"
            },
            "status": {
                "health": "GET /health",
                "model_status": "GET /model-status"
            }
        },
        "note": "This is a pure API backend. Frontend is deployed separately on Vercel."
    }

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    """Serve index page if frontend is available (local dev only)"""
    if templates is None:
        return JSONResponse(
            {"error": "Frontend not available. This is an API-only deployment. Visit /docs for API documentation."},
            status_code=404
        )
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/learn", response_class=HTMLResponse)
async def learn(request: Request):
    """Serve learn page if frontend is available (local dev only)"""
    if templates is None:
        return JSONResponse(
            {"error": "Frontend not available. This is an API-only deployment."},
            status_code=404
        )
    try:
        return templates.TemplateResponse("learn_new.html", {"request": request})
    except:
        return templates.TemplateResponse("learn.html", {"request": request})

@app.get("/classroom", response_class=HTMLResponse)
async def classroom_home(request: Request):
    """Serve classroom page if frontend is available (local dev only)"""
    if templates is None:
        return JSONResponse(
            {"error": "Frontend not available. This is an API-only deployment."},
            status_code=404
        )
    return templates.TemplateResponse("classroom_home.html", {"request": request})

@app.get("/teacher", response_class=HTMLResponse)
async def teacher_dashboard(request: Request, room_id: Optional[str] = None):
    """Serve teacher page if frontend is available (local dev only)"""
    if templates is None:
        return JSONResponse(
            {"error": "Frontend not available. This is an API-only deployment."},
            status_code=404
        )
    if not room_id:
        room_id = secrets.token_hex(3).upper()
    logger.info(f"🎤 Teacher dashboard opened with room_id: {room_id}")
    return templates.TemplateResponse("teacher.html", {"request": request, "room_id": room_id})

@app.get("/student", response_class=HTMLResponse)
async def student_dashboard(request: Request, room_id: Optional[str] = None):
    """Serve student page if frontend is available (local dev only)"""
    if templates is None:
        return JSONResponse(
            {"error": "Frontend not available. This is an API-only deployment."},
            status_code=404
        )
    if not room_id:
        raise HTTPException(status_code=400, detail="Room ID required")
    logger.info(f"👁️ Student dashboard opened for room_id: {room_id}")
    return templates.TemplateResponse("student.html", {"request": request, "room_id": room_id})

@app.post("/infer-frame")
async def infer_frame(frame: UploadFile = File(...), return_annotated: bool = Form(False)):
    """Accept a single image frame and return detection JSON"""
    t0 = time.time()
    try:
        if model is None:
            return JSONResponse({'error': 'Model not loaded', 'model_loaded': False}, status_code=503)

        file_bytes = await frame.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        if img is None:
            return JSONResponse({'error': 'Could not decode image'}, status_code=415)

        t1 = time.time()
        result = run_inference_on_frame(img)
        t2 = time.time()

        response_data = {
            'detected_sign': result['detected_sign'],
            'confidence': result['confidence'],
            'detections': result['detections'],
            'timing': {'decode': t1 - t0, 'inference': t2 - t1, 'total': t2 - t0}
        }

        if return_annotated and 'annotated_frame' in result:
            _, buffer = cv.imencode('.jpg', result['annotated_frame'])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            response_data['annotated_frame'] = f"data:image/jpeg;base64,{frame_base64}"

        return JSONResponse(response_data)
    except Exception as e:
        logger.error("/infer-frame error: %s\n%s", str(e), traceback.format_exc())
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/infer-letter")
async def infer_letter(frame: UploadFile = File(...), return_annotated: bool = Form(False)):
    """Accept a single image frame and return letter detection JSON"""
    t0 = time.time()
    try:
        if letter_model is None:
            return JSONResponse({'error': 'Letter model not loaded', 'model_loaded': False}, status_code=503)

        file_bytes = await frame.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        if img is None:
            return JSONResponse({'error': 'Could not decode image'}, status_code=415)

        t1 = time.time()
        result = run_letter_inference_on_frame(img)
        t2 = time.time()

        response_data = {
            'detected_letter': result['detected_letter'],
            'confidence': result['confidence'],
            'detections': result['detections'],
            'timing': {'decode': t1 - t0, 'inference': t2 - t1, 'total': t2 - t0}
        }

        if return_annotated and 'annotated_frame' in result:
            _, buffer = cv.imencode('.jpg', result['annotated_frame'])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            response_data['annotated_frame'] = f"data:image/jpeg;base64,{frame_base64}"

        return JSONResponse(response_data)
    except Exception as e:
        logger.error("/infer-letter error: %s\n%s", str(e), traceback.format_exc())
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get("/model-status")
async def model_status():
    gesture_classes = []
    if model is not None and hasattr(model, 'classes_'):
        gesture_classes = model.classes_.tolist()
    
    letter_classes = []
    if letter_model is not None and hasattr(letter_model, 'classes_'):
        letter_classes = letter_model.classes_.tolist()
    
    return JSONResponse({
        'ml_libraries_available': True,
        'gesture_model_loaded': model is not None,
        'letter_model_loaded': letter_model is not None,
        'model_type': '.pkl',
        'gesture_classes': gesture_classes,
        'letter_classes': letter_classes,
        'gesture_actions_count': len(gesture_classes),
        'letter_actions_count': len(letter_classes),
        'demo_mode': model is None and letter_model is None
    })

@app.get("/health")
async def health_check():
    return JSONResponse({'status': 'ok', 'model_loaded': model is not None})

@app.post("/process-confirmed-words")
async def process_confirmed_words(request: Request):
    try:
        data = await request.json()
        confirmed_words = data.get('confirmedWords')
        
        if not isinstance(confirmed_words, list) or not confirmed_words:
            return JSONResponse({'error': 'Invalid or missing "confirmedWords"'}, status_code=400)

        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key or not openai_key.strip():
            fallback = ' '.join(confirmed_words).title()
            return JSONResponse({'sentence': fallback})

        try:
            from services.revtrans import gloss_to_english_llm
            sentence = gloss_to_english_llm(confirmed_words)
            return JSONResponse({'sentence': sentence})
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            fallback = ' '.join(confirmed_words).title()
            return JSONResponse({'sentence': fallback})

    except Exception as e:
        logger.error(f"Handler exception: {e}")
        return JSONResponse({'error': 'Internal server error'}, status_code=500)

@app.post("/reverse-translate-video")
async def reverse_translate_video(request: Request):
    try:
        data = await request.json()
        gloss_tokens = data.get('glossTokens')
        text = data.get('text')

        if isinstance(text, str) and text.strip():
            try:
                from services.revtrans import sentence_to_gloss_tokens as _sentence_to_gloss_tokens
                available = _list_available_video_tokens()
                gloss_tokens = _sentence_to_gloss_tokens(text.strip(), available_tokens=available)
            except Exception:
                gloss_tokens = _text_to_gloss_tokens(text)

        if not isinstance(gloss_tokens, list) or not gloss_tokens:
            available = _list_available_video_tokens()[:30]
            return JSONResponse({'error': 'Invalid payload', 'available_tokens_preview': available}, status_code=400)

        fname, meta = compose_video_from_gloss(gloss_tokens)
        url = f"/outputs/{fname}"

        return JSONResponse({
            'video_url': url,
            'file': os.path.basename(fname),
            'meta': meta,
            'tokens': gloss_tokens
        })

    except FileNotFoundError as e:
        return JSONResponse({'error': str(e)}, status_code=404)
    except Exception as e:
        logger.error(f'/reverse-translate-video error: {e}\n{traceback.format_exc()}')
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get("/outputs/{filename}")
async def serve_output_file(filename: str, request: Request):
    """Serve generated files from outputs/ with HTTP Range support for videos"""
    full_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(full_path):
        return JSONResponse({'error': 'File not found'}, status_code=404)

    range_header = request.headers.get('range')
    if not range_header:
        return FileResponse(full_path)

    try:
        units, rng = range_header.split('=', 1)
        if units.strip().lower() != 'bytes':
            raise ValueError('Only bytes unit is supported')
        start_str, end_str = (rng.split('-', 1) + [''])[:2]
        file_size = os.path.getsize(full_path)
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
        start = max(0, start)
        end = min(end, file_size - 1)
        length = (end - start) + 1

        def iterfile():
            with open(full_path, 'rb') as f:
                f.seek(start)
                yield f.read(length)

        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(length),
        }
        return StreamingResponse(iterfile(), status_code=206, media_type='video/mp4', headers=headers)
    except Exception as e:
        logger.warning(f'Range request failed: {e}')
        return FileResponse(full_path)

# ==================== CHROME EXTENSION ENDPOINTS ====================

@app.post("/tokenize-text")
async def tokenize_text(request: Request):
    """
    Tokenize text into ASL gloss tokens for Chrome extension.
    Returns available tokens that have video files.
    """
    try:
        data = await request.json()
        text = data.get('text', '').strip()
        
        if not text:
            return JSONResponse({'error': 'No text provided'}, status_code=400)
        
        logger.info(f"🔤 Tokenizing text: '{text}'")
        
        # Get available video tokens
        available_tokens = _list_available_video_tokens()
        
        # Convert text to gloss tokens using LLM if available
        try:
            from services.revtrans import sentence_to_gloss_tokens as _sentence_to_gloss_tokens
            gloss_tokens = _sentence_to_gloss_tokens(text, available_tokens=available_tokens)
        except Exception as e:
            logger.warning(f"LLM tokenization failed, using simple split: {e}")
            gloss_tokens = _text_to_gloss_tokens(text)
        
        # Filter to only tokens with available videos
        available_gloss = [t for t in gloss_tokens if t.lower() in [a.lower() for a in available_tokens]]
        missing = [t for t in gloss_tokens if t.lower() not in [a.lower() for a in available_tokens]]
        
        logger.info(f"✅ Tokenized: {len(available_gloss)} available, {len(missing)} missing")
        
        return JSONResponse({
            'tokens': available_gloss,  # Tokens with videos
            'tokens_all': gloss_tokens,  # All tokens from LLM
            'missing': missing,  # Tokens without videos
            'available': available_tokens[:50]  # Sample of available tokens
        })
        
    except Exception as e:
        logger.error(f"❌ Tokenize text error: {e}\n{traceback.format_exc()}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post("/batch-token-videos")
async def batch_token_videos(request: Request):
    """
    Get video URLs for multiple tokens at once (optimized for Chrome extension).
    Returns URLs that the extension can fetch directly.
    """
    try:
        data = await request.json()
        tokens = data.get('tokens', [])
        
        if not tokens:
            return JSONResponse({'error': 'No tokens provided'}, status_code=400)
        
        logger.info(f"📦 Batch video request for {len(tokens)} tokens")
        
        from services.dynamic_video_fetcher import WLASLVideoFetcher
        fetcher = WLASLVideoFetcher()
        
        result = {}
        for token in tokens:
            token_lower = token.lower()
            try:
                # This downloads and caches the video
                video_paths = fetcher.get_video_paths_for_gloss(token_lower, source="aslbrick", max_videos=1)
                
                if video_paths and os.path.exists(video_paths[0]):
                    # Return the API endpoint URL, not the file path
                    result[token] = f"/token-video/{token_lower}"
                    logger.debug(f"✅ Video ready for token: {token}")
                else:
                    result[token] = None
                    logger.debug(f"❌ No video for token: {token}")
            except Exception as e:
                logger.warning(f"⚠️ Error fetching video for '{token}': {e}")
                result[token] = None
        
        available_count = sum(1 for v in result.values() if v is not None)
        logger.info(f"✅ Batch complete: {available_count}/{len(tokens)} videos available")
        
        return JSONResponse({'videos': result})
        
    except Exception as e:
        logger.error(f"❌ Batch video error: {e}\n{traceback.format_exc()}")
        return JSONResponse({'error': str(e)}, status_code=500)

@app.get("/token-video/{token}")
async def get_token_video(token: str):
    """
    Get video file for a specific ASL token (for Chrome extension).
    Downloads from WLASL if necessary and serves the video file.
    """
    try:
        logger.info(f"🎥 Requesting video for token: '{token}'")
        token_lower = token.lower()
        
        # Try to fetch from WLASL (uses cached version if already downloaded)
        try:
            from services.dynamic_video_fetcher import WLASLVideoFetcher
            fetcher = WLASLVideoFetcher()
            
            # This downloads the video and returns the local file path
            video_paths = fetcher.get_video_paths_for_gloss(token_lower, source="aslbrick", max_videos=1)
            
            if video_paths and os.path.exists(video_paths[0]):
                video_file = video_paths[0]
                logger.info(f"✅ Serving video file: {video_file}")
                return FileResponse(
                    video_file, 
                    media_type='video/mp4',
                    headers={
                        "Accept-Ranges": "bytes",
                        "Cache-Control": "public, max-age=3600"
                    }
                )
        except Exception as e:
            logger.warning(f"⚠️ WLASL fetch failed: {e}")
        
        # Video not found
        logger.warning(f"❌ No video found for token: '{token}'")
        return JSONResponse({'error': f'Video not found for token: {token}'}, status_code=404)
        
    except Exception as e:
        logger.error(f"❌ Token video error: {e}\n{traceback.format_exc()}")
        return JSONResponse({'error': str(e)}, status_code=500)

# ==================== WEBSOCKET ROUTES ====================

@app.websocket("/ws/classroom/{room_id}/teacher")
async def websocket_teacher(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id, is_teacher=True)
    try:
        await websocket.send_json({
            'type': 'teacher_connected',
            'room_id': room_id,
            'message': 'Connected. Waiting for students...'
        })
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'send_speech':
                try:
                    audio_base64 = data.get('audio')
                    text = transcribe_audio(audio_base64)
                    
                    try:
                        from services.revtrans import sentence_to_gloss_tokens as _sentence_to_gloss_tokens
                        available_tokens = _list_available_video_tokens()
                        gloss_tokens = _sentence_to_gloss_tokens(text, available_tokens=available_tokens)
                    except Exception:
                        gloss_tokens = _text_to_gloss_tokens(text)
                    
                    fname, meta = compose_video_from_gloss(gloss_tokens)
                    video_url = f"/outputs/{fname}"
                    
                    # Send caption to teacher
                    await websocket.send_json({
                        'type': 'caption_received',
                        'text': text,
                        'timestamp': datetime.utcnow().isoformat(),
                        'tokens': gloss_tokens
                    })
                    
                    # Broadcast video to students
                    await manager.broadcast_to_room(room_id, {
                        'type': 'video_broadcast',
                        'video_url': video_url,
                        'duration': meta.get('frames', 0) / meta.get('fps', 25),
                        'tokens': gloss_tokens,
                        'text': text
                    })
                    
                except Exception as e:
                    await websocket.send_json({'type': 'error', 'message': str(e)})
                    
    except WebSocketDisconnect:
        logger.info(f"Teacher disconnected from room {room_id}")

@app.websocket("/ws/classroom/{room_id}/student")
async def websocket_student(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id, is_teacher=False)
    try:
        await websocket.send_json({
            'type': 'student_connected',
            'room_id': room_id,
            'message': 'Connected to classroom'
        })
        
        # Notify teacher
        if room_id in active_classrooms and active_classrooms[room_id].get('teacher'):
            teacher_ws = active_classrooms[room_id]['teacher']
            await teacher_ws.send_json({
                'type': 'student_joined',
                'count': len(active_classrooms[room_id]['students'])
            })
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        logger.info(f"Student disconnected from room {room_id}")

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Sign Language Translator API")
    logger.info(f"✅ Temporary output directory: {OUTPUT_DIR}")
    logger.info(f"⚠️ Note: Files in {OUTPUT_DIR} are ephemeral and will be lost on restart")
    logger.info(f"✅ Frontend directory: {FRONTEND_DIR}")
    if model:
        logger.info("✅ Gesture model loaded")
    if letter_model:
        logger.info("✅ Letter model loaded")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
