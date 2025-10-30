from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import hashlib
import shutil  # for moving generated videos
import os
import tempfile
import logging
import io
import time
import traceback
import json
import secrets
import base64
# ML / CV deps
import numpy as np
import cv2 as cv
import torch
#import albumentations as A
#from albumentations.pytorch import ToTensorV2
import traceback
import joblib
import mediapipe as mp
import math
import difflib


mp_drawing = mp.solutions.drawing_utils


# Avoid importing revtrans at module import time because it asserts OPENAI_API_KEY.
# We'll import within request handlers when needed.

# Project model/utils
#from model import DETR
try:
    from utils.setup import get_classes, get_colors
    from utils.boxes import rescale_bboxes
except Exception:  # Fallbacks if utils not available
    def get_classes():
        return ["class_0", "class_1", "class_2"]
    def get_colors():
        return [(0,255,0), (255,0,0), (0,0,255)]
    def rescale_bboxes(bboxes, size_hw):
        # assume normalized cxcywh -> xyxy in pixel space, passthrough if already pixel
        H, W = size_hw
        b = bboxes.detach().cpu().numpy()
        if b.shape[-1] == 4:
            # If already looks like xyxy in pixels, just return tensor-like np
            return torch.tensor(b)
        return torch.tensor(b)

print("✅ ML dependencies loaded successfully")

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for all routes

# ============ WEBSOCKET SETUP FOR CLASSROOM FEATURE ============
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# In-memory session storage for classrooms
# Structure: { "ROOM_ID": { "teacher": sid, "students": [sid1, sid2, ...] } }
active_classrooms = {}

print("✅ WebSocket (SocketIO) initialized for classroom feature")
# ============ END WEBSOCKET SETUP ============

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_IMAGE_MIME = {"image/jpeg", "image/png"}
CONFIDENCE_THRESHOLD = 0.8

# Output directory for generated artifacts (e.g., composed videos)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Simple in-memory cache mapping text->deterministic output file for reverse translation segments
_REVERSE_SEGMENT_CACHE: dict[str, str] = {}

# Simple token normalization/mapping helpers to improve coverage
def _stem_token(w: str) -> str:
    w = w.lower().strip()
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w

def _map_tokens_to_available(tokens: list[str], available: list[str]):
    """Return (mapped:list[str], missing:list[str]). Try simple stemming and fallbacks.

    Mapping rules:
      - If token present, keep
      - Else try stemmed form
      - Else try common synonyms (limited, editable)
      - Else mark as missing (caller may skip or display)
    """
    avail = set([a.lower() for a in available])
    mapped = []
    missing = []

    # lightweight, user-editable synonyms (extend as you add videos)
    SYN = {
        'those': 'they',
        'these': 'they',
        'them': 'they',
        'people': 'they',
        'achieve': 'success',
        'achievement': 'success',
        'great': 'good',
        'nice': 'good',
        'things': 'thing',
        'stuff': 'thing',
        'life': 'live',
        'today': 'day',
        'exam': 'test',
        'always': 'always',
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
        # Try fuzzy match as last resort
        close = difflib.get_close_matches(t0, list(avail), n=1, cutoff=0.86)
        if close:
            mapped.append(close[0])
            continue
        missing.append(t0)
    return mapped, missing

#model loading
#mp_hands = mp.solutions.hands
#hands = mp_hands.Hands(max_num_hands=2,
#                       min_detection_confidence=0.7,
#                       min_tracking_confidence=0.7)


mp_hands = mp.solutions.hands

# Model Loading
MODEL_FILE = "./pretrained/gesture_model.pkl"
try:
    model = joblib.load(MODEL_FILE)
    print("✅ PKL Model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load PKL model: {e}")
    model = None

# Letter Model Loading
LETTER_MODEL_FILE = "./pretrained/letter_model.pkl"
try:
    letter_model = joblib.load(LETTER_MODEL_FILE)
    print("✅ Letter PKL Model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load Letter PKL model: {e}")
    letter_model = None



# Add these utility functions after the model loading:

def normalize_landmarks(landmarks):
    """
    Normalize landmarks like during training:
    - Translate so wrist is at origin.
    - Scale by wrist → middle finger MCP distance.
    """
    wrist = landmarks[0]
    translated = [(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z) for lm in landmarks]

    scale = math.sqrt(translated[9][0]**2 + translated[9][1]**2 + translated[9][2]**2)
    if scale < 1e-6:
        scale = 1.0

    normalized = [(x/scale, y/scale, z/scale) for (x, y, z) in translated]
    return [coord for triple in normalized for coord in triple]

def empty_hand():
    return [0.0] * (21 * 3)


# Replace the entire run_inference_on_frame function:

def run_inference_on_frame(frame_bgr: np.ndarray):
    """Run model inference on a single BGR frame and return best detection with hand landmarks drawn.

    Returns dict: {detected_sign, confidence, detections: [...], annotated_frame} or None if no detection.
    """
    global model
    if model is None:
        raise RuntimeError("Model not loaded")

    # Create a new MediaPipe hands instance for each request to avoid timestamp conflicts
    hands = mp_hands.Hands(max_num_hands=2,
                          min_detection_confidence=0.7,
                          min_tracking_confidence=0.7)

    try:
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Create a copy of the frame for annotation
        annotated_frame = frame_bgr.copy()

        left_hand, right_hand = None, None

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                label = handedness.classification[0].label  # "Left" or "Right"
                score = handedness.classification[0].score

                if score < 0.7:
                    continue  # skip low-confidence

                # Draw hand landmarks on the annotated frame - THIS WAS MISSING!
                mp_drawing.draw_landmarks(
                    annotated_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
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

        # Only predict if at least one hand is visible
        if any(v != 0.0 for v in features[0]):
            pred = model.predict(features)[0]

            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features).max()
                confidence = float(proba)
                text = f"Gesture: {pred} ({confidence:.2f})"
            else:
                confidence = 1.0
                text = f"Gesture: {pred}"

            # Add text overlay on the annotated frame
            cv.putText(annotated_frame, text, (10, 40),
                      cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

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
        # Clean up the MediaPipe instance
        hands.close()

        
@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/about')
def about():
    return render_template('about.html')


@app.route('/learn')
def learn():
    # Prefer the newer page if present
    try:
        return render_template('learn_new.html')
    except Exception:
        return render_template('learn.html')


# ============ CLASSROOM ROUTES ============

@app.route('/classroom')
def classroom_home():
    """Home page to choose role (teacher or student)"""
    return render_template('classroom_home.html')


@app.route('/teacher')
def teacher_dashboard():
    """Teacher dashboard - speech input interface"""
    room_id = request.args.get('room_id') or secrets.token_hex(3).upper()
    logger.info(f"🎤 Teacher dashboard opened with room_id: {room_id}")
    return render_template('teacher.html', room_id=room_id)


@app.route('/student')
def student_dashboard():
    """Student dashboard - video display interface"""
    room_id = request.args.get('room_id')
    if not room_id:
        logger.warning("❌ Student tried to join without room_id")
        return "Room ID required. Use /student?room_id=ABC123", 400
    
    logger.info(f"👁️ Student dashboard opened for room_id: {room_id}")
    return render_template('student.html', room_id=room_id)

# ============ END CLASSROOM ROUTES ============


# Replace the infer_frame function:

@app.route('/infer-frame', methods=['POST'])
def infer_frame():
    """Accept a single image frame (jpeg/png) and return detection JSON with optional annotated frame."""
    t0 = time.time()
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'model_loaded': False
            }), 503

        if 'frame' not in request.files:
            return jsonify({'error': 'No frame provided (expect form-data field "frame")'}), 400

        file = request.files['frame']
        if file.mimetype not in ALLOWED_IMAGE_MIME:
            return jsonify({'error': f'Unsupported content type: {file.mimetype}'}), 415

        # Read image bytes into numpy array
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
        if frame is None:
            return jsonify({'error': 'Could not decode image'}), 415

        t1 = time.time()
        result = run_inference_on_frame(frame)
        t2 = time.time()

        # Check if client wants annotated frame
        return_annotated = request.form.get('return_annotated', 'false').lower() == 'true'
        
        response_data = {
            'detected_sign': result['detected_sign'],
            'confidence': result['confidence'],
            'detections': result['detections'],
            'timing': {
                'decode': t1 - t0,
                'inference': t2 - t1,
                'total': t2 - t0
            }
        }

        if return_annotated and 'annotated_frame' in result:
            # Encode annotated frame as base64 JPEG
            import base64
            _, buffer = cv.imencode('.jpg', result['annotated_frame'])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            response_data['annotated_frame'] = f"data:image/jpeg;base64,{frame_base64}"

        return jsonify(response_data)
    except Exception as e:
        logger.error("/infer-frame error: %s\n%s", str(e), traceback.format_exc())
        return jsonify({'error': str(e)}), 500
# Replace the model_status function:

@app.route('/model-status', methods=['GET'])
def model_status():
    # Get gesture model classes
    gesture_classes = []
    if model is not None and hasattr(model, 'classes_'):
        gesture_classes = model.classes_.tolist()
    elif model is not None:
        gesture_classes = ["gesture_class"]
    
    # Get letter model classes
    letter_classes = []
    if letter_model is not None and hasattr(letter_model, 'classes_'):
        letter_classes = letter_model.classes_.tolist()
    elif letter_model is not None:
        letter_classes = ["A", "B", "C"]  # fallback
    
    return jsonify({
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
# Replace the health_check function:

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'model_loaded': model is not None})

@app.route('/test-llm', methods=['GET', 'POST'])
def test_llm():
    """Test endpoint to manually check LLM calls"""
    try:
        logger.info("🧪 TEST-LLM endpoint called")
        
        # Check environment
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            return jsonify({
                'error': 'No OpenAI API key found',
                'env_check': False
            }), 400
        
        logger.info("🔑 OpenAI API key found (length: %d)", len(openai_key))
        
        # Test import
        try:
            from revtrans import text_to_gloss, gloss_to_english_llm, sentence_to_gloss_tokens
            logger.info("✅ Successfully imported LLM functions")
        except Exception as e:
            logger.error("❌ Failed to import LLM functions: %s", e)
            return jsonify({
                'error': f'Import failed: {e}',
                'import_check': False
            }), 500
        
        # Test basic LLM call
        test_sentence = "We are going to college"
        logger.info("🧪 Testing with sentence: %s", test_sentence)
        
        # Test text_to_gloss
        gloss_result = text_to_gloss(test_sentence)
        logger.info("✅ text_to_gloss result: %s", gloss_result)
        
        # Test sentence_to_gloss_tokens
        available_tokens = _list_available_video_tokens()
        tokens_result = sentence_to_gloss_tokens(test_sentence, available_tokens)
        logger.info("✅ sentence_to_gloss_tokens result: %s", tokens_result)
        
        # Test gloss_to_english_llm
        test_tokens = ["we", "go", "college"]
        english_result = gloss_to_english_llm(test_tokens)
        logger.info("✅ gloss_to_english_llm result: %s", english_result)
        
        return jsonify({
            'status': 'success',
            'env_check': True,
            'import_check': True,
            'test_input': test_sentence,
            'text_to_gloss': gloss_result,
            'sentence_to_gloss_tokens': tokens_result,
            'gloss_to_english_llm': english_result,
            'available_tokens_count': len(available_tokens)
        }), 200
        
    except Exception as e:
        logger.error("❌ LLM test failed: %s", str(e))
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500




def run_letter_inference_on_frame(frame_bgr: np.ndarray):
    """Run letter model inference on a single BGR frame and return detected letter.

    Returns dict: {detected_letter, confidence, detections: [...], annotated_frame} or None if no detection.
    """
    print("🔤 run_letter_inference_on_frame called!")  # Debug print
    global letter_model
    if letter_model is None:
        print("❌ Letter model is None!")  # Debug print
        raise RuntimeError("Letter model not loaded")

    # Create a new MediaPipe hands instance for each request
    hands = mp_hands.Hands(max_num_hands=1,  # Letters typically use one hand
                          min_detection_confidence=0.7,
                          min_tracking_confidence=0.7)

    try:
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Create a copy of the frame for annotation
        annotated_frame = frame_bgr.copy()

        if results.multi_hand_landmarks and results.multi_handedness:
            hand_landmarks = results.multi_hand_landmarks[0]  # Use first hand
            handedness = results.multi_handedness[0]
            
            if handedness.classification[0].score >= 0.7:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    annotated_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
                )

                # Normalize landmarks for letter model
                norm = normalize_landmarks(hand_landmarks.landmark)
                features = np.array([norm])

                # Predict letter
                pred = letter_model.predict(features)[0]
                print(f"🔤 Predicted letter: {pred}")  # Debug print

                if hasattr(letter_model, "predict_proba"):
                    proba = letter_model.predict_proba(features).max()
                    confidence = float(proba)
                    text = f"Letter: {pred} ({confidence:.2f})"
                    print(f"🔤 Confidence: {confidence:.2f}")  # Debug print
                else:
                    confidence = 1.0
                    text = f"Letter: {pred}"
                    print(f"🔤 No probability available, using confidence: 1.0")  # Debug print

                # Add text overlay
                cv.putText(annotated_frame, text, (10, 40),
                          cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

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

@app.route('/test-letter-model', methods=['GET'])
def test_letter_model():
    """Test if letter model is loaded and working"""
    try:
        if letter_model is None:
            return jsonify({
                'status': 'error',
                'message': 'Letter model not loaded'
            }), 503
            
        # Test with dummy data
        import numpy as np
        dummy_features = np.zeros((1, 63))  # 21 landmarks * 3 coordinates
        pred = letter_model.predict(dummy_features)[0]
        
        return jsonify({
            'status': 'success',
            'message': 'Letter model is working',
            'dummy_prediction': str(pred),
            'model_type': str(type(letter_model))
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/infer-letter', methods=['POST'])
def infer_letter():
    """Accept a single image frame and return letter detection JSON with optional annotated frame."""
    print("🔤 /infer-letter endpoint called!")  # Debug print
    t0 = time.time()
    try:
        if letter_model is None:
            return jsonify({
                'error': 'Letter model not loaded',
                'model_loaded': False
            }), 503

        if 'frame' not in request.files:
            return jsonify({'error': 'No frame provided (expect form-data field "frame")'}), 400

        file = request.files['frame']
        if file.mimetype not in ALLOWED_IMAGE_MIME:
            return jsonify({'error': f'Unsupported content type: {file.mimetype}'}), 415

        # Read image bytes into numpy array
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
        if frame is None:
            return jsonify({'error': 'Could not decode image'}), 415

        t1 = time.time()
        result = run_letter_inference_on_frame(frame)
        t2 = time.time()

        # Check if client wants annotated frame
        return_annotated = request.form.get('return_annotated', 'false').lower() == 'true'
        
        response_data = {
            'detected_letter': result['detected_letter'],
            'confidence': result['confidence'],
            'detections': result['detections'],
            'timing': {
                'decode': t1 - t0,
                'inference': t2 - t1,
                'total': t2 - t0
            }
        }

        if return_annotated and 'annotated_frame' in result:
            # Encode annotated frame as base64 JPEG
            import base64
            _, buffer = cv.imencode('.jpg', result['annotated_frame'])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            response_data['annotated_frame'] = f"data:image/jpeg;base64,{frame_base64}"

        return jsonify(response_data)
    except Exception as e:
        logger.error("/infer-letter error: %s\n%s", str(e), traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Payload too large'}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404



@app.route('/process-confirmed-words', methods=['POST'])
def process_confirmed_words():
    logger.info("[LLM Flow] ◀️ Enter /process-confirmed-words")
    try:
        # Force parse JSON or throw
        data = request.get_json(force=True)
        logger.info("[LLM Flow] 📨 Raw JSON payload: %r", data)

        confirmed_words = data.get('confirmedWords')
        if not isinstance(confirmed_words, list) or not confirmed_words:
            logger.warning("[LLM Flow] ⚠️ Invalid confirmedWords: %r", confirmed_words)
            return jsonify({
                'error': 'Invalid or missing "confirmedWords". Expected a non-empty list.'
            }), 400

        logger.info("[LLM Flow] 🔍 confirmedWords list: %r", confirmed_words)

        # Fallback if no API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key or not openai_key.strip():
            logger.warning("[LLM Flow] 🔑 OPENAI_API_KEY missing, using fallback")
            fallback = ' '.join(confirmed_words).title()
            logger.info("[LLM Flow] ✅ Fallback sentence: %r", fallback)
            return jsonify({'sentence': fallback}), 200

        # Attempt LLM call
        try:
            logger.info("[LLM Flow] 🤖 Importing gloss_to_english_llm")
            from revtrans import gloss_to_english_llm
            logger.info("[LLM Flow] 🤖 Calling LLM with tokens: %r", confirmed_words)
            sentence = gloss_to_english_llm(confirmed_words)
            logger.info("[LLM Flow] ✅ LLM returned: %r", sentence)
            return jsonify({'sentence': sentence}), 200

        except ImportError as ie:
            logger.error("[LLM Flow] ❌ revtrans import error: %s", ie)
        except Exception as e:
            logger.error("[LLM Flow] ❌ LLM call error: %s\n%s", e, traceback.format_exc())

        # Final fallback
        fallback = ' '.join(confirmed_words).title()
        logger.info("[LLM Flow] ✅ Final fallback sentence: %r", fallback)
        return jsonify({'sentence': fallback}), 200

    except Exception as e:
        logger.error("[LLM Flow] Handler exception: %s\n%s", e, traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500
    
@app.route('/outputs/<path:filename>', methods=['GET'])
def serve_output_file(filename: str):
    """Serve generated files from outputs/ with basic HTTP Range support for videos.

    Many browsers request video files with Range headers. If we detect a Range request,
    return a 206 Partial Content response with appropriate headers; otherwise fall back
    to a normal send_from_directory.
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404

    range_header = request.headers.get('Range', None)
    if not range_header:
        resp = send_from_directory(OUTPUT_DIR, filename, as_attachment=False)
        # Advertise support for ranges to help the <video> element
        try:
            resp.headers.add('Accept-Ranges', 'bytes')
        except Exception:
            pass
        return resp

    # Parse Range header: e.g. "bytes=START-END"
    try:
        # Expected format 'bytes=start-end'
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

        with open(full_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)

        resp = Response(data, 206, mimetype='video/mp4', direct_passthrough=True)
        resp.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
        resp.headers.add('Accept-Ranges', 'bytes')
        resp.headers.add('Content-Length', str(length))
        return resp
    except Exception as e:
        logger.warning('Range request failed, falling back to full file: %s', e)
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


def _list_available_video_tokens() -> list[str]:
    """Return available token basenames from WLASL mapper and local videos directory.
    
    Prioritizes WLASL glosses (2000+) but includes local videos as fallback.
    """
    tokens = set()
    
    # Try to get WLASL glosses
    try:
        from dynamic_video_fetcher import WLASLVideoFetcher
        fetcher = WLASLVideoFetcher()
        # Get all glosses from the index
        wlasl_glosses = list(fetcher.gloss_index.keys())
        tokens.update(wlasl_glosses)
        logger.info(f"✅ Loaded {len(wlasl_glosses)} glosses from WLASL mapper")
    except Exception as e:
        logger.warning(f"⚠️ Could not load WLASL glosses: {e}")
    
    # Also add local videos as fallback
    base_vid_dir = os.path.join(os.path.dirname(__file__), 'videos')
    if os.path.isdir(base_vid_dir):
        for name in os.listdir(base_vid_dir):
            if name.lower().endswith('.mp4'):
                tokens.add(os.path.splitext(name)[0].lower())
        logger.info(f"✅ Added {len([n for n in os.listdir(base_vid_dir) if n.endswith('.mp4')])} local videos")
    
    return sorted(tokens)


def _text_to_gloss_tokens(text: str) -> list[str]:
    """Convert a free-form sentence into a list of gloss-like tokens, aligned to available clips.

    Strategy:
    - Lowercase and strip punctuation
    - Simple stemming for common endings (ing/ed/s)
    - Drop stopwords
    - Keep only tokens that have a matching videos/<token>.mp4 clip
    """
    if not text:
        return []
    import re

    # Normalize
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9'\s]", " ", s)
    words = [w for w in re.split(r"\s+", s) if w]

    # Simple contractions map and lemmatization hints
    contr = {
        "i'm": "i", "im": "i", "we're": "we", "you're": "you", "they're": "they",
        "can't": "cannot", "won't": "will", "don't": "do", "doesn't": "do", "didn't": "do",
    }
    words = [contr.get(w, w) for w in words]

    # Basic stemming try
    def stem(w: str) -> str:
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > 3 and w.endswith(suf):
                return w[: -len(suf)]
        return w

    # Stopwords (keep short list)
    stop = {"the", "a", "an", "is", "am", "are", "to", "at", "in", "on", "for", "of", "and", "or", "with", "be", "was", "were", "will", "would", "should", "could", "have", "has", "had", "do", "did", "does", "that", "this", "these", "those", "it"}

    candidates = [stem(w) for w in words if w not in stop]

    avail = set(_list_available_video_tokens())
    filtered = [w for w in candidates if w in avail]
    # If nothing matched, return the raw candidates to allow caller to handle missing clips
    return filtered or candidates


# ============ CLASSROOM FEATURE HELPER FUNCTIONS ============

def transcribe_audio(audio_base64: str) -> str:
    """Convert base64-encoded audio data to text using OpenAI Whisper API.
    
    Args:
        audio_base64: Base64-encoded audio data (webm, wav, mp3, etc.)
    
    Returns:
        Transcribed text string
    
    Raises:
        Exception: If OpenAI API call fails or audio is invalid
    """
    try:
        logger.info("🎤 Transcribing audio via OpenAI Whisper...")
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"
        
        # Call OpenAI Whisper API
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        
        text = transcript.text.strip()
        logger.info(f"✅ Transcription complete: '{text}'")
        return text
        
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        raise


# ============ END CLASSROOM HELPER FUNCTIONS ============


def compose_video_from_gloss(gloss_tokens):
    """Concatenate per-token mp4 clips from WLASL JSON mapper into a single mp4 in outputs.
    
    Uses the dynamic_video_fetcher to fetch videos on-demand from WLASL dataset.
    Returns (filename, meta) where filename is the saved file name under OUTPUT_DIR.
    """
    # Try to use WLASL fetcher first
    try:
        from dynamic_video_fetcher import WLASLVideoFetcher
        fetcher = WLASLVideoFetcher()
        logger.info("✅ Using WLASL fetcher to load videos")
    except Exception as e:
        logger.warning(f"⚠️ WLASL fetcher unavailable: {e}, falling back to local videos")
        fetcher = None
    
    files = []
    missing = []
    
    # Fetch videos using WLASL mapper or fallback to local
    for t in gloss_tokens:
        name = str(t).strip().lower()
        if not name:
            continue
        
        try:
            if fetcher:
                # Try WLASL fetcher first
                logger.info(f"📹 Fetching video from WLASL for token: '{name}'")
                videos = fetcher.get_video_paths_for_gloss(name, source="aslbrick", max_videos=1)
                if videos:
                    files.extend(videos)
                    logger.info(f"✅ Found {len(videos)} video(s) from WLASL for '{name}'")
                else:
                    logger.warning(f"⚠️ No WLASL video found for '{name}', checking local...")
                    raise Exception("No WLASL video found")
            else:
                raise Exception("Fetcher not available")
        except Exception as e:
            # Fallback to local videos
            logger.info(f"🔄 Falling back to local video for '{name}': {e}")
            base_vid_dir = os.path.join(os.path.dirname(__file__), 'videos')
            cand = os.path.join(base_vid_dir, f"{name}.mp4")
            if os.path.exists(cand):
                files.append(cand)
                logger.info(f"✅ Found local video for '{name}': {cand}")
            else:
                missing.append(name)
                logger.warning(f"❌ No video found for '{name}' (neither WLASL nor local)")

    if not files:
        available_tokens = _list_available_video_tokens()
        raise FileNotFoundError(f"No matching video clips found for tokens: {gloss_tokens}. Available tokens: {available_tokens[:10]}...")

    # Open first clip to get properties
    first = cv.VideoCapture(files[0])
    if not first.isOpened():
        raise RuntimeError(f"Could not open first video clip: {files[0]}")
    fps = first.get(cv.CAP_PROP_FPS) or 25.0
    width = int(first.get(cv.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(first.get(cv.CAP_PROP_FRAME_HEIGHT) or 480)
    first.release()
    
    logger.info(f"Video properties: {width}x{height}, {fps} FPS")

    # Prepare writer
    out_name = f"reverse_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.mp4"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    
    # Use H.264 codec which is universally supported by browsers
    fourcc = cv.VideoWriter_fourcc(*'avc1')  # H.264 codec
    writer = cv.VideoWriter(out_path, fourcc, fps, (width, height))
    
    if not writer.isOpened():
        # Try alternative H.264 codec identifier
        fourcc = cv.VideoWriter_fourcc(*'H264')
        writer = cv.VideoWriter(out_path, fourcc, fps, (width, height))
        
    if not writer.isOpened():
        # Final fallback to MP4V
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        writer = cv.VideoWriter(out_path, fourcc, fps, (width, height))
        
    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video writer at {out_path}")
    
    logger.info(f"Created video writer: {out_path} with codec: {fourcc}")

    total_frames = 0
    processed_files = 0
    try:
        for fp in files:
            logger.info(f"Processing video file: {fp}")
            cap = cv.VideoCapture(fp)
            if not cap.isOpened():
                logger.warning("Skip unreadable clip: %s", fp)
                continue
            
            file_frames = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                # Ensure frame is the right size
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv.resize(frame, (width, height))
                writer.write(frame)
                total_frames += 1
                file_frames += 1
            cap.release()
            processed_files += 1
            logger.info(f"Processed {file_frames} frames from {os.path.basename(fp)}")
            
        # If we have no frames, add a placeholder black frame to prevent empty video
        if total_frames == 0:
            logger.warning("No frames processed, adding placeholder frame")
            black_frame = np.zeros((height, width, 3), dtype=np.uint8)
            for _ in range(int(fps)):  # 1 second of black frames
                writer.write(black_frame)
                total_frames += 1
    finally:
        writer.release()
        logger.info(f"Video composition complete: {total_frames} total frames from {processed_files} files")

    meta = { 'fps': fps, 'width': width, 'height': height, 'frames': total_frames, 'missing': missing, 'codec': 'avc1' }
    if total_frames == 0:
        # Clean up empty file and surface a clear error
        try:
            if os.path.exists(out_path):
                os.remove(out_path)
        except Exception:
            pass
        raise RuntimeError("Output video had 0 frames. Check source clips and codecs.")
    return out_name, meta


def _compose_segment_from_text_cached(text: str, use_llm: bool = True):
    """Compose a short reverse-translation video for a single text segment, with caching.

    Returns tuple: (filename, meta, tokens)
    - Uses a deterministic filename based on SHA1 of normalized text to allow reuse across requests.
    - Attempts LLM tokenization when available (and use_llm=True), else falls back to heuristic tokenization.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Invalid text segment")

    norm_text = ' '.join(text.strip().split()).lower()
    # Deterministic filename for caching
    key = hashlib.sha1(norm_text.encode('utf-8')).hexdigest()
    out_name = f"seg_{key}.mp4"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    # If already composed and non-empty, reuse
    if os.path.isfile(out_path) and os.path.getsize(out_path) > 0:
        # best-effort meta reconstruction isn't possible here without parsing; return minimal
        return out_name, { 'cached': True }, []

    # Convert text to gloss tokens
    tokens = None
    if use_llm:
        try:
            from revtrans import sentence_to_gloss_tokens as _sentence_to_gloss_tokens
            available = _list_available_video_tokens()
            tokens = _sentence_to_gloss_tokens(norm_text, available_tokens=available)
        except Exception:
            tokens = None
    if not tokens:
        tokens = _text_to_gloss_tokens(norm_text)

    if not isinstance(tokens, list) or not tokens:
        raise FileNotFoundError("No valid gloss tokens could be derived from text")

    # Compose to a temporary file and then move to deterministic cache path
    tmp_name, meta = compose_video_from_gloss(tokens)
    tmp_path = os.path.join(OUTPUT_DIR, tmp_name)
    try:
        shutil.move(tmp_path, out_path)
    except Exception:
        # If move fails but file exists, keep temp name as fallback
        out_name = tmp_name
        out_path = tmp_path

    return out_name, meta, tokens


@app.route('/reverse-translate-video', methods=['POST'])
def reverse_translate_video():
    try:
        data = request.get_json(silent=True) or {}
        logger.info(f"🎬 reverse_translate_video called with data: {data}")
        gloss_tokens = data.get('glossTokens')
        text = data.get('text')
        logger.info(f"📝 gloss_tokens: {gloss_tokens}, text: {text}")

        # Prefer sentence input via revtrans if provided
        if isinstance(text, str) and text.strip():
            try:
                logger.info("🤖 Attempting to import LLM function: sentence_to_gloss_tokens")
                from revtrans import sentence_to_gloss_tokens as _sentence_to_gloss_tokens
                logger.info("✅ LLM function imported successfully")
            except Exception as ie:
                logger.warning('❌ revtrans.sentence_to_gloss_tokens import failed, falling back: %s', ie)
                _sentence_to_gloss_tokens = None

            if _sentence_to_gloss_tokens is not None:
                available = _list_available_video_tokens()
                logger.info("🤖 Making LLM call to convert text to gloss tokens: %s", text.strip())
                gloss_tokens = _sentence_to_gloss_tokens(text.strip(), available_tokens=available)
                logger.info("✅ LLM returned gloss tokens: %s", gloss_tokens)
            else:
                logger.info("🔄 Using fallback text processing (no LLM)")
                gloss_tokens = _text_to_gloss_tokens(text)

        if not isinstance(gloss_tokens, list) or not gloss_tokens:
            available = _list_available_video_tokens()[:30]
            logger.warning(f"❌ Invalid payload. Available tokens: {available}")
            return jsonify({
                'error': 'Invalid payload. Provide a sentence via "text" or a token list "glossTokens".',
                'hint': 'Example text: "We go college" or glossTokens: ["we", "go", "college"]',
                'available_tokens_preview': available
            }), 400

        # ✅ Compose video from gloss tokens
        logger.info(f"🎥 Composing video from tokens: {gloss_tokens}")
        fname, meta = compose_video_from_gloss(gloss_tokens)
        logger.info(f"✅ Video composed: {fname}, meta: {meta}")

        # ✅ Use existing /outputs/<filename> route (no moving needed)
        url = f"/outputs/{fname}"
        logger.info(f"🌐 Video URL: {url}")

        # Warn clearly if codec is not H.264 which some browsers require
        if meta.get('codec') and meta['codec'].lower() not in ('avc1', 'h264', 'x264', 'mp4v'):
            meta['playback_warning'] = 'Browser may not play this codec. Prefer H.264 (avc1).'

        return jsonify({
            'video_url': url,
            'file': os.path.basename(fname),
            'meta': meta,
            'tokens': gloss_tokens
        }), 200

    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        tb = traceback.format_exc()
        logger.error('/reverse-translate-video error: %s\n%s', str(e), tb)
        return jsonify({'error': str(e), 'trace': tb}), 500


@app.route('/token-video/<token>', methods=['GET'])
def serve_token_video(token: str):
    """Serve a single token clip videos/<token>.mp4 if exists."""
    base_vid_dir = os.path.join(os.path.dirname(__file__), 'videos')
    safe_token = os.path.basename(token).lower()
    fname = f"{safe_token}.mp4"
    full_path = os.path.join(base_vid_dir, fname)
    if not os.path.isfile(full_path):
        return jsonify({'error': 'Token clip not found', 'token': safe_token}), 404
    try:
        # Use send_from_directory to avoid path traversal
        return send_from_directory(base_vid_dir, fname, as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reverse-translate-segment', methods=['POST'])
def reverse_translate_segment():
    """Compose a cached reverse-translation clip for a single transcript segment.

    Request JSON: { text: string, use_llm?: bool }
    Response 200: { video_url, file, meta, tokens }
    """
    try:
        data = request.get_json(force=True)
        text = (data.get('text') or '').strip()
        use_llm = bool(data.get('use_llm', True))

        if not text:
            return jsonify({'error': 'Missing text'}), 400

        fname, meta, tokens = _compose_segment_from_text_cached(text, use_llm=use_llm)
        url = f"/outputs/{fname}"
        return jsonify({
            'video_url': url,
            'file': os.path.basename(fname),
            'meta': meta,
            'tokens': tokens
        }), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        tb = traceback.format_exc()
        logger.error('/reverse-translate-segment error: %s\n%s', str(e), tb)
        return jsonify({'error': str(e), 'trace': tb}), 500


@app.route('/reverse-translate-transcript', methods=['POST'])
def reverse_translate_transcript():
    """Batch compose reverse-translation clips for a transcript with timestamps.

    Request JSON: { segments: [{ start: number, end: number, text: string }], use_llm?: bool }
    Response 200: { results: [{ start, end, text, video_url, file, tokens, meta }] }
    Notes:
      - Processes sequentially; uses cached composition when available.
      - Intended for prefetching; for strict "real-time" sync, call per-segment just-in-time.
    """
    try:
        data = request.get_json(force=True)
        segments = data.get('segments')
        use_llm = bool(data.get('use_llm', True))
        if not isinstance(segments, list) or not segments:
            return jsonify({'error': 'Provide non-empty segments list'}), 400

        results = []
        for seg in segments:
            text = (seg.get('text') or '').strip() if isinstance(seg, dict) else ''
            if not text:
                results.append({ 'error': 'Empty text', **({k:v for k,v in seg.items()} if isinstance(seg, dict) else {}) })
                continue
            try:
                fname, meta, tokens = _compose_segment_from_text_cached(text, use_llm=use_llm)
                results.append({
                    'start': float(seg.get('start', 0)) if isinstance(seg, dict) else 0,
                    'end': float(seg.get('end', 0)) if isinstance(seg, dict) else 0,
                    'text': text,
                    'video_url': f"/outputs/{fname}",
                    'file': os.path.basename(fname),
                    'tokens': tokens,
                    'meta': meta
                })
            except Exception as e:
                results.append({
                    'start': float(seg.get('start', 0)) if isinstance(seg, dict) else 0,
                    'end': float(seg.get('end', 0)) if isinstance(seg, dict) else 0,
                    'text': text,
                    'error': str(e)
                })

        return jsonify({ 'results': results }), 200
    except Exception as e:
        tb = traceback.format_exc()
        logger.error('/reverse-translate-transcript error: %s\n%s', str(e), tb)
        return jsonify({'error': str(e), 'trace': tb}), 500
    
# ============ WEBSOCKET EVENT HANDLERS FOR CLASSROOM ============

@socketio.on('teacher_join')
def handle_teacher_join(data):
    """Teacher connects to a classroom room"""
    try:
        room_id = data.get('room_id')
        if not room_id:
            emit('error', {'message': 'room_id required'})
            return
        
        if room_id not in active_classrooms:
            active_classrooms[room_id] = {'teacher': None, 'students': []}
        
        active_classrooms[room_id]['teacher'] = request.sid
        join_room(room_id)
        
        logger.info(f"✅ Teacher joined room {room_id}")
        emit('teacher_connected', {
            'room_id': room_id,
            'message': 'Connected. Waiting for students...'
        })
    except Exception as e:
        logger.error(f"❌ teacher_join error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('student_join')
def handle_student_join(data):
    """Student connects to a classroom room"""
    try:
        room_id = data.get('room_id')
        if not room_id:
            emit('error', {'message': 'room_id required'})
            return
        
        if room_id not in active_classrooms:
            active_classrooms[room_id] = {'teacher': None, 'students': []}
        
        active_classrooms[room_id]['students'].append(request.sid)
        join_room(room_id)
        
        student_count = len(active_classrooms[room_id]['students'])
        logger.info(f"✅ Student joined room {room_id} (Total: {student_count})")
        
        emit('student_connected', {
            'room_id': room_id,
            'message': 'Connected to classroom'
        })
        
        # Notify teacher of new student
        if active_classrooms[room_id]['teacher']:
            emit('student_joined', {
                'count': student_count,
                'message': f'Student {student_count} joined'
            }, room=active_classrooms[room_id]['teacher'])
    except Exception as e:
        logger.error(f"❌ student_join error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('send_speech')
def handle_send_speech(data):
    """Process teacher's speech and broadcast video to students"""
    try:
        room_id = data.get('room_id')
        audio_base64 = data.get('audio')
        
        if not room_id or not audio_base64:
            emit('error', {'message': 'room_id and audio required'})
            return
        
        logger.info(f"🎤 Processing speech from room {room_id}")
        
        # STEP 1: Transcribe audio
        try:
            text = transcribe_audio(audio_base64)
            logger.info(f"📝 Transcribed: {text}")
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            emit('error', {'message': f'Transcription failed: {str(e)}'})
            return
        
        # STEP 2: Convert text to gloss tokens
        try:
            from revtrans import sentence_to_gloss_tokens as _sentence_to_gloss_tokens
            available_tokens = _list_available_video_tokens()
            gloss_tokens = _sentence_to_gloss_tokens(text, available_tokens=available_tokens)
            logger.info(f"🤖 Gloss tokens: {gloss_tokens}")
        except Exception as e:
            logger.warning(f"⚠️ LLM conversion failed, using fallback: {e}")
            gloss_tokens = _text_to_gloss_tokens(text)
            logger.info(f"🤖 Fallback tokens: {gloss_tokens}")
        
        # STEP 3: Compose video from gloss tokens
        try:
            fname, meta = compose_video_from_gloss(gloss_tokens)
            video_url = f"/outputs/{fname}"
            logger.info(f"🎬 Video composed: {video_url}")
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            emit('error', {'message': f'Video composition failed: {str(e)}'})
            return
        
        # STEP 4: Send caption to teacher
        emit('caption_received', {
            'text': text,
            'timestamp': datetime.utcnow().isoformat(),
            'tokens': gloss_tokens
        }, room=active_classrooms[room_id].get('teacher'))
        
        # STEP 5: Broadcast video to all students
        emit('video_broadcast', {
            'video_url': video_url,
            'duration': meta.get('duration_seconds', meta.get('frames', 0) / meta.get('fps', 25)),
            'tokens': gloss_tokens,
            'text': text
        }, room=room_id)
        
        logger.info(f"✅ Broadcast complete to {len(active_classrooms[room_id]['students'])} students")
        
    except Exception as e:
        logger.error(f"❌ send_speech error: {e}\n{traceback.format_exc()}")
        emit('error', {'message': str(e)})


@socketio.on('disconnect')
def handle_disconnect():
    """Clean up when user disconnects"""
    try:
        logger.info(f"✗ Client disconnected: {request.sid}")
        
        for room_id, session in active_classrooms.items():
            # If teacher left
            if session.get('teacher') == request.sid:
                logger.info(f"  Teacher left room {room_id}")
                active_classrooms[room_id]['teacher'] = None
            
            # If student left
            if request.sid in session.get('students', []):
                session['students'].remove(request.sid)
                logger.info(f"  Student left room {room_id} ({len(session['students'])} remaining)")
                
                # Notify teacher
                if session.get('teacher'):
                    emit('student_left', {
                        'count': len(session['students'])
                    }, room=session['teacher'])
    except Exception as e:
        logger.error(f"❌ disconnect error: {e}")


# ============ END WEBSOCKET EVENT HANDLERS ============

# Replace the main block:

if __name__ == '__main__':
    print("🚀 Starting Sign Language Translator with Classroom Feature...")
    print("📁 Loading PKL model...")

    if model is not None:
        print("✅ PKL Model ready!")
    else:
        print("⚠️ PKL Model failed to load. Endpoints will return 503 for inference.")

    print("🌐 Starting Flask + SocketIO server...")
    print("📌 Classroom Features:")
    print("   - Teacher: http://localhost:5000/teacher")
    print("   - Student: http://localhost:5000/student?room_id=ABC123")
    print("   - Home: http://localhost:5000/classroom")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
