# Classroom Feature Implementation Plan

## 📋 Project Analysis Overview

### Current System Architecture

Your project has these key components:

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT INTELLIFY                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FLASK BACKEND (app.py)                                    │
│  ├─ /reverse-translate-video (POST)                         │
│  │  └─ Takes text/gloss tokens → generates video            │
│  ├─ /reverse-translate-segment (POST)                       │
│  ├─ /infer-frame (POST) - hand gesture detection            │
│  ├─ /infer-letter (POST) - letter recognition               │
│  └─ /outputs/<filename> (GET) - serve videos                │
│                                                              │
│  TEXT → GLOSS CONVERSION (revtrans.py)                     │
│  ├─ sentence_to_gloss_tokens() - uses OpenAI GPT-4o-mini   │
│  ├─ text_to_gloss()                                         │
│  └─ gloss_to_english_llm()                                  │
│                                                              │
│  VIDEO COMPOSITION (app.py)                                │
│  ├─ compose_video_from_gloss() - concatenates MP4 clips     │
│  └─ _list_available_video_tokens() - discovers videos/      │
│                                                              │
│  DATA LAYER                                                 │
│  ├─ videos/ (800+ MP4 clips) - organized by gloss token     │
│  ├─ outputs/ - generated video cache                        │
│  ├─ pretrained/ - ML models (gesture_model, letter_model)   │
│  └─ templates/ (index.html, learn.html)                     │
│                                                              │
│  CURRENT ML FEATURES                                        │
│  ├─ Real-time hand detection (MediaPipe)                    │
│  ├─ Gesture classification (joblib model)                   │
│  └─ Letter recognition (MediaPipe + joblib model)           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Proposed Classroom Feature

### Use Case
- **Teacher**: Speaks via microphone
  - Speech transcribed to text (Whisper API or local)
  - Text converted to sign language gloss tokens (GPT-4o-mini)
  - Video clips stitched together
  - Captions displayed in real-time
  - Video broadcast to all connected students

- **Students**: Watch sign language video clips
  - Receive broadcast video URL instantly
  - Play video synchronized
  - See transcript/captions
  - Real-time experience with 1:N communication

---

## 🏗️ Implementation Plan (Step-by-Step)

### **Phase 1: Add Flask-SocketIO Support** ✅ (5-10 minutes)

**Files to Modify:**
- `app.py` - Add WebSocket server

**What to add:**
```
1. Import flask-socketio at top
2. Initialize SocketIO instance with CORS
3. Create in-memory classroom session storage (dictionary)
4. Add 3 new SocketIO event handlers:
   - @socketio.on('teacher_join') - teacher enters room
   - @socketio.on('student_join') - student enters room
   - @socketio.on('send_speech') - teacher sends audio
   - @socketio.on('disconnect') - cleanup when disconnected
```

**No Breaking Changes:**
- All existing routes stay the same
- Just adding new WebSocket layer on top

---

### **Phase 2: Create New Flask Routes** ✅ (5 minutes)

**Files to Modify:**
- `app.py`

**What to add:**
```
1. @app.route('/classroom') - home page to choose role
2. @app.route('/teacher') - teacher dashboard
   - Input: room_id (URL param or generated)
   - Output: teacher.html with room_id
3. @app.route('/student') - student dashboard
   - Input: room_id (REQUIRED in URL)
   - Output: student.html with room_id
```

**Example URLs:**
- `http://localhost:5000/teacher` → Creates new room with random ID
- `http://localhost:5000/teacher?room_id=ABC123` → Join specific room
- `http://localhost:5000/student?room_id=ABC123` → Join as student
- `http://localhost:5000/classroom` → Home page

---

### **Phase 3: Add Speech-to-Text Helper** ✅ (3-5 minutes)

**Files to Create or Modify:**
- `app.py` - Add new helper function

**What to add:**
```python
def transcribe_audio(audio_base64):
    """
    Convert base64 audio to text using OpenAI Whisper
    
    Input: Base64-encoded audio data (webm/wav)
    Output: Transcribed text string
    
    Option A (Cloud): Use OpenAI Whisper API (1 API call per speech)
    Option B (Local): Use local Whisper model (free, no API calls)
    """
```

**No changes needed to existing code** - just a new helper function

---

### **Phase 4: Create Teacher UI** ✅ (10-15 minutes)

**Files to Create:**
- `templates/teacher.html`

**What it includes:**
```
1. Header
   - Room code display (for students to join)
   - Student count counter
   - End session button

2. Microphone Section
   - Start/Stop recording button
   - Recording status indicator
   - Waveform visualization (optional)

3. Live Captions Display
   - Shows real-time caption of recognized speech
   - Caption history panel

4. Processing Status
   - Speech Recognition: Ready/Processing/Done
   - Video Generation: Ready/Processing/Done
   - Broadcast: Ready/Processing/Done

5. JavaScript
   - Connect to WebSocket
   - Record audio from mic
   - Send audio to server
   - Listen for caption updates
   - Update UI in real-time
```

**Dependencies:**
- Uses browser Microphone API (getUserMedia)
- Uses Socket.IO client library
- No new packages needed

---

### **Phase 5: Create Student UI** ✅ (10-15 minutes)

**Files to Create:**
- `templates/student.html`

**What it includes:**
```
1. Header
   - Room code display
   - Connection status indicator
   - Leave button

2. Video Display Section
   - Placeholder: "Waiting for teacher..."
   - Video player with controls
   - Auto-play when video arrives

3. Transcript Panel
   - Shows history of all glosses received
   - Timestamp for each
   - Duration of each video

4. JavaScript
   - Connect to WebSocket with room_id
   - Listen for video_broadcast events
   - Auto-play received video
   - Update transcript history
```

**Dependencies:**
- Uses Socket.IO client library
- No new packages needed

---

### **Phase 6: Create Home Page** ✅ (5 minutes)

**Files to Create:**
- `templates/classroom_home.html`

**What it includes:**
```
1. Role Selection
   - "Teacher" button → /teacher
   - "Student" button → prompts for room code

2. OR Quick Start
   - Generate Room ID
   - Show QR code (optional) for students to scan

3. Simple CSS styling
```

---

### **Phase 7: Update requirements.txt** ✅ (1 minute)

**Files to Modify:**
- `requirements.txt` (or `setup.py`)

**Add these packages:**
```
flask-socketio==5.3.4
python-socketio==5.10.0
python-engineio==4.7.1
```

**Note:** OpenAI package already in use, Whisper API uses existing client

---

## 🔄 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   CLASSROOM SESSION                      │
│                                                          │
│   TEACHER                      SERVER              STUDENTS
│   (Browser)                  (Flask+SocketIO)    (Browsers)
│                                                          │
│      │                            │                      │
│      ├─ /teacher ────────────→    │                      │
│      │                            │                      │
│      │ WebSocket: teacher_join    │                      │
│      ├───────────────────────────→│                      │
│      │                            │                      │
│      │                            │◄─ /student?room_id   │
│      │                            │ ◄────────────────────┤
│      │                            │                      │
│      │                            │ WebSocket: student_join
│      │                            │ ◄────────────────────┤
│      │                            │                      │
│      │                        Emit: student_joined       │
│      │◄───────────────────────────┤                      │
│      │ (Update count)              │                      │
│      │                            │                      │
│  [TEACHER SPEAKS]                │                      │
│      │                            │                      │
│      │ WebSocket: send_speech     │                      │
│      │ (audio base64) ──────────→ │                      │
│      │                            │                      │
│      │                  ┌─────────────────┐              │
│      │                  │ 1. Transcribe   │              │
│      │                  │    (Whisper)    │              │
│      │                  ├─────────────────┤              │
│      │                  │ 2. Get gloss    │              │
│      │                  │    (GPT-4o)     │              │
│      │                  ├─────────────────┤              │
│      │                  │ 3. Compose      │              │
│      │                  │    video        │              │
│      │                  └─────────────────┘              │
│      │                            │                      │
│      │ Emit: caption_received     │                      │
│      │◄───────────────────────────┤                      │
│      │ "Hello everyone"           │                      │
│      │                            │                      │
│      │                        Emit: video_broadcast     │
│      │                            │─────────────────────→│
│      │                            │  /outputs/xxx.mp4    │
│      │                            │                      │
│      │                            │ [VIDEO PLAYS]        │
│      │                            │                      │
│      │                            │ [AUTO-ADD TO        │
│      │                            │  TRANSCRIPT]         │
│      │                            │                      │
│      └────────────────────────────┴──────────────────────┘
```

---

## 🔑 Key Implementation Details

### **WebSocket Events Reference**

```python
# TEACHER EVENTS
socketio.on('teacher_join')
├─ Input: { room_id: "ABC123" }
└─ Stores: active_classrooms[room_id]['teacher'] = sid

socketio.on('send_speech')
├─ Input: { room_id: "ABC123", audio: "<base64>" }
└─ Processing: transcribe → gloss → compose → broadcast

# STUDENT EVENTS
socketio.on('student_join')
├─ Input: { room_id: "ABC123" }
├─ Stores: active_classrooms[room_id]['students'].append(sid)
└─ Emits: student_joined to teacher

# SERVER BROADCASTS
emit('caption_received', {...})
├─ Target: Only the teacher
└─ Data: { text: "...", timestamp }

emit('video_broadcast', {...})
├─ Target: All users in room (teacher + students)
└─ Data: { video_url, duration, tokens }

emit('student_joined', {...})
├─ Target: Only the teacher
└─ Data: { count: 5 }
```

---

## 📦 New Files to Create

```
templates/
├─ classroom_home.html          (20 lines) - Role selection
├─ teacher.html                 (150 lines) - Teacher dashboard
└─ student.html                 (120 lines) - Student dashboard

static/
└─ classroom.css                (200 lines) - Styles for classroom

(Total new code: ~490 lines)
```

---

## 🔧 Files to Modify (Existing)

```
app.py
├─ Add imports (flask-socketio)
├─ Initialize SocketIO instance
├─ Add 4 new routes: /classroom, /teacher, /student, (+ WebSocket handlers)
├─ Add transcribe_audio() helper
└─ Active classrooms dict for session management

(Additions: ~100-150 lines)

requirements.txt or setup.py
└─ Add 3 new packages
```

---

## ⚠️ What Does NOT Need to Change

✅ **NO Changes Needed to:**
- `revtrans.py` - Already has LLM functions
- `model.py` - ML models stay the same
- `app.py` existing routes - All still work
- `/reverse-translate-video` - Can reuse it
- Video library structure - No reorganization needed
- Database - No DB needed (in-memory storage)

---

## 🚀 Execution Timeline

| Phase | Task | Time | Files |
|-------|------|------|-------|
| 1 | Add SocketIO to app.py | 5-10 min | app.py |
| 2 | Create routes (/teacher, /student) | 5 min | app.py |
| 3 | Add transcribe_audio() helper | 3-5 min | app.py |
| 4 | Build teacher.html UI | 10-15 min | teacher.html |
| 5 | Build student.html UI | 10-15 min | student.html |
| 6 | Build classroom_home.html | 5 min | classroom_home.html |
| 7 | Create classroom.css | 10 min | classroom.css |
| 8 | Update requirements.txt | 1 min | requirements.txt |
| 9 | Test end-to-end | 15-30 min | All files |
| **Total** | | **60-90 min** | **7 files** |

---

## 💡 Technology Stack Summary

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Real-time Communication** | Flask-SocketIO | WebSocket protocol |
| **Speech Recognition** | OpenAI Whisper API | ~$0.02 per minute |
| **Text → Gloss** | OpenAI GPT-4o-mini | Already integrated |
| **Video Composition** | OpenCV | Already integrated |
| **Video Storage** | MP4 in `/videos/` | ~800 clips, no changes |
| **Session Storage** | In-Memory Dict | No DB needed |
| **Frontend** | HTML5 + Vanilla JS | WebSocket client |

---

## 🎯 Success Criteria

After implementation, you should be able to:

1. ✅ Teacher opens `/teacher` → Gets random room code (e.g., "ABC123")
2. ✅ Students open `/student?room_id=ABC123` → Connect to same room
3. ✅ Teacher clicks "Start Recording" → Records microphone
4. ✅ Teacher stops recording → Audio sent to server
5. ✅ Server:
   - Transcribes audio ("Hello class")
   - Converts to gloss (["hello", "class"])
   - Composes video (/outputs/reverse_20251030_103045_123456.mp4)
   - Broadcasts video URL to all students
6. ✅ Teacher sees caption: "Hello class"
7. ✅ All students automatically play video
8. ✅ Students see in transcript: "HELLO → CLASS" with timestamp
9. ✅ Loop back to step 3 for next utterance

---

## 🔐 Security Notes (Phase 2+)

For production deployment:
- Add room code validation (e.g., 6-character alphanumeric)
- Add teacher authentication (simple PIN or OAuth)
- Add timeout cleanup for abandoned rooms
- Rate limit speech processing (prevent spam)

For MVP: No security needed (classroom is local)

---

## 📝 Next Steps

1. **Review this plan** with you
2. **Start Phase 1** → Modify app.py for SocketIO
3. **Create new routes** (Phase 2)
4. **Build UI templates** (Phases 4-6)
5. **Test end-to-end** with 1 teacher + 2-3 students
6. **Iterate** based on feedback

---

## 🤔 Questions to Clarify

1. **Speech Recognition:** Use Whisper API (cloud) or local model?
   - Cloud = $0.02/min, instant, no setup
   - Local = Free, but needs local model (~1.5GB)

2. **UI Preferences:** Should we follow existing Intellify design (dark theme) or create new style?

3. **Testing:** Do you have a local server running? Or deploy to cloud first?

---

**Ready to start Phase 1?** 🚀
