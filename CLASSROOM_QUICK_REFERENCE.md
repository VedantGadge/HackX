# 📋 Classroom Implementation - Quick Reference Checklist

## 🔍 Project Analysis Complete ✅

Your current Intellify system has everything needed:

- ✅ **Speech-to-gloss conversion**: `revtrans.py` uses GPT-4o-mini
- ✅ **Video composition**: `compose_video_from_gloss()` in app.py
- ✅ **Video library**: 800+ MP4 clips in `/videos/`
- ✅ **FastAPI backend**: Flask with existing routes
- ✅ **ML models**: Hand detection, gesture, letter recognition

---

## 📦 What's Already There (No Changes Needed)

| Component | File | Status | Action |
|-----------|------|--------|--------|
| Text to Gloss LLM | `revtrans.py` | Ready | **Reuse as-is** |
| Video Composition | `app.py` | Ready | **Reuse as-is** |
| Video Library | `/videos/` | Ready | **No changes** |
| Flask Server | `app.py` | Ready | **Add SocketIO** |
| HTML Templates | `templates/` | Ready | **Keep existing** |

---

## 🆕 What's New (7 Files Total)

### Files to MODIFY (2)
1. **app.py** - Add ~150 lines for SocketIO + routes + helpers
2. **requirements.txt** - Add 3 packages

### Files to CREATE (5)
1. **templates/classroom_home.html** - Role selection (20 lines)
2. **templates/teacher.html** - Teacher UI (150 lines)
3. **templates/student.html** - Student UI (120 lines)
4. **static/classroom.css** - Styles (200 lines)
5. *(Optional)* **static/classroom.js** - Extract JS to separate file

---

## 🎯 Implementation Phases (Simple to Complex)

```
Phase 1: Add SocketIO Support (app.py)
  ├─ Import flask-socketio
  ├─ Initialize SocketIO instance
  ├─ Create active_classrooms dict
  └─ Time: 5-10 min

Phase 2: Create Routes (app.py)
  ├─ @app.route('/classroom') - home
  ├─ @app.route('/teacher') - teacher dash
  └─ @app.route('/student') - student dash
  └─ Time: 5 min

Phase 3: Add Speech-to-Text Helper (app.py)
  ├─ def transcribe_audio(audio_base64)
  └─ Time: 3-5 min

Phase 4: WebSocket Event Handlers (app.py)
  ├─ @socketio.on('teacher_join')
  ├─ @socketio.on('student_join')
  ├─ @socketio.on('send_speech') ← Main processing
  └─ @socketio.on('disconnect')
  └─ Time: 10-15 min

Phase 5: Teacher HTML UI (teacher.html)
  ├─ Microphone controls
  ├─ Caption display
  ├─ Student counter
  └─ Time: 15 min

Phase 6: Student HTML UI (student.html)
  ├─ Video player
  ├─ Transcript panel
  ├─ Connection indicator
  └─ Time: 15 min

Phase 7: Styling (classroom.css)
  ├─ Responsive design
  ├─ Dark theme (match existing)
  └─ Time: 10 min

Phase 8: Update Dependencies
  ├─ requirements.txt
  └─ Time: 1 min

TOTAL: ~60-90 minutes
```

---

## 🔑 Core Logic Walkthrough

### When Teacher Speaks

```python
@socketio.on('send_speech')
def handle_speech(data):
    room_id = data['room_id']
    audio_base64 = data['audio']  # Browser sent this
    
    # STEP 1: TRANSCRIBE
    text = transcribe_audio(audio_base64)
    print(f"📝 Transcribed: {text}")
    # Output: "Hello everyone, welcome to class"
    
    # STEP 2: GET GLOSS (EXISTING revtrans.py)
    from revtrans import sentence_to_gloss_tokens
    available_tokens = _list_available_video_tokens()
    gloss_tokens = sentence_to_gloss_tokens(text, available_tokens)
    print(f"🤖 Gloss: {gloss_tokens}")
    # Output: ["hello", "everyone", "welcome", "class"]
    
    # STEP 3: COMPOSE VIDEO (EXISTING app.py)
    fname, meta = compose_video_from_gloss(gloss_tokens)
    video_url = f"/outputs/{fname}"
    print(f"🎬 Video: {video_url}")
    # Output: "/outputs/reverse_20251030_103045_123456.mp4"
    
    # STEP 4: SEND CAPTION TO TEACHER
    emit('caption_received', 
        {'text': text, 'timestamp': now},
        room=teacher_sid)
    
    # STEP 5: BROADCAST VIDEO TO ALL (teacher + students)
    emit('video_broadcast',
        {'video_url': video_url, 'tokens': gloss_tokens},
        room=room_id)  # Sends to ENTIRE ROOM
```

That's the entire flow! Rest is just UI/plumbing.

---

## 📡 WebSocket Event Map

```
BROWSER (Teacher)                FLASK SERVER                BROWSER (Students)
     │                                 │                            │
     ├─ teacher_join ────────────────→ │                            │
     │                                 │ (stores teacher_sid)       │
     │                                 │                            │
     │                                 │ ←──────── student_join ────┤
     │                                 │           (S1)             │
     │ emit: student_joined ←──────────┤                            │
     │      { count: 1 }               │                            │
     │                                 │                            │
     │                                 │ ←──────── student_join ────┤
     │                                 │           (S2)             │
     │ emit: student_joined ←──────────┤                            │
     │      { count: 2 }               │                            │
     │                                 │                            │
     │ send_speech ───────────────────→│                            │
     │ {audio}                         │ [PROCESSING: 2-3 sec]      │
     │                                 │ 1. Transcribe              │
     │                                 │ 2. Gloss                   │
     │                                 │ 3. Video                   │
     │                                 │                            │
     │ ←─ caption_received ────────────┤                            │
     │ "Hello everyone"                │ ──→ video_broadcast ──────→ │
     │                                 │     /outputs/xxx.mp4       │
     │                                 │                            │
     │                                 │                 [Auto-play]│
     │                                 │                            │
     │ (Loop: speak again)             │         (Add to transcript)│
```

---

## 💾 Code Files Reference

### app.py - Existing Functions YOU CAN REUSE

```python
# ALREADY EXISTS - DO NOT MODIFY:
_list_available_video_tokens()      # Lists available video tokens
compose_video_from_gloss()          # Concatenates MP4 clips
_text_to_gloss_tokens()             # Fallback text processing

# EXISTING ROUTES - WILL STAY UNCHANGED:
@app.route('/reverse-translate-video', methods=['POST'])
@app.route('/reverse-translate-segment', methods=['POST'])
@app.route('/infer-frame', methods=['POST'])
@app.route('/infer-letter', methods=['POST'])
@app.route('/outputs/<filename>')   # Video file serving

# YOU ONLY ADD:
from flask_socketio import SocketIO, emit, join_room, leave_room
socketio = SocketIO(app, cors_allowed_origins="*")
active_classrooms = {}

@app.route('/classroom')
@app.route('/teacher')
@app.route('/student')

@socketio.on('teacher_join')
@socketio.on('student_join')
@socketio.on('send_speech')
@socketio.on('disconnect')

def transcribe_audio(audio_base64):
```

### revtrans.py - Existing LLM Functions YOU REUSE

```python
# ALREADY EXISTS - WILL BE IMPORTED:
sentence_to_gloss_tokens(sentence, available_tokens)
    ↓
text_to_gloss(sentence)  # Uses GPT-4o-mini internally
```

---

## 🧪 Testing Workflow

### Local Testing (Single Machine)

```bash
# Terminal 1: Start Flask server with SocketIO
python app.py

# Browser 1: Teacher
http://localhost:5000/teacher
→ Copy room code (e.g., ABC123)

# Browser 2: Student
http://localhost:5000/student?room_id=ABC123

# Browser 3: Another Student (optional)
http://localhost:5000/student?room_id=ABC123

# In Teacher Browser:
→ Click "Start Recording"
→ Speak: "Hello students"
→ Click "Stop"
→ Wait 2-3 seconds for processing

# In Both Student Browsers:
→ Should see video auto-play
→ Should add to transcript
```

### Testing Checklist

- [ ] Teacher can join → Gets room code
- [ ] Students can join → Connect to room
- [ ] Teacher browser shows student count
- [ ] Start/Stop recording button works
- [ ] Audio captured successfully
- [ ] Processing completes in 2-3 sec
- [ ] Caption appears in teacher browser
- [ ] Video URL generated
- [ ] Video plays in student browsers
- [ ] Video added to transcript
- [ ] Multiple utterances work
- [ ] Closing browser disconnects
- [ ] Reconnecting doesn't break anything

---

## 🐛 Debugging Checklist

If something doesn't work:

| Issue | Cause | Solution |
|-------|-------|----------|
| Room code doesn't generate | `secrets` module not imported | Add `import secrets` |
| WebSocket won't connect | SocketIO not initialized | Check `socketio = SocketIO(...)` |
| Audio not captured | Microphone permission denied | Check browser console |
| Transcription fails | OpenAI API key missing | Verify `OPENAI_API_KEY` env var |
| Video not composing | Videos not found | Check `/videos/` folder has files |
| Video doesn't broadcast | emit() to wrong room | Should be `emit(..., room=room_id)` |
| Students don't see video | Browser console JS errors | Open DevTools (F12) |

---

## 📊 System Requirements

### Server
- Python 3.8+
- Flask (already have)
- OpenCV (already have)
- torch/MediaPipe (already have)
- **NEW**: flask-socketio, python-socketio, python-engineio

### Client (Browser)
- HTML5 support (getUserMedia for mic)
- WebSocket support (Socket.IO JS client)
- MP4 video player (all browsers)
- Any modern browser: Chrome, Firefox, Safari, Edge

### Network
- Server must be accessible to all students (same LAN or public URL)
- WebSocket port open (same as Flask port, usually 5000)
- Audio streaming bandwidth: ~100 KB/s (Opus codec)

---

## 🚀 Deployment Notes

### Local Development
```bash
python app.py
# Runs on http://localhost:5000
# Share room code verbally with students on same network
```

### Production (Heroku)
```bash
# Add Procfile:
web: gunicorn --worker-class eventlet -w 1 app:app

# Deploy:
git push heroku main
```

### Production (Docker)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 📈 Performance Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Speech to caption | < 3s | ✅ Achievable |
| Caption to students | < 500ms | ✅ WebSocket fast |
| Video composition | 2-5s | ✅ Depends on # videos |
| Concurrent students | 100+ | ✅ WebSocket scales |
| Latency per broadcast | < 100ms | ✅ Same server room |

---

## 🎓 Educational Features (Future Enhancements)

After MVP, can add:
- [ ] Record session for playback
- [ ] Q&A with voting
- [ ] Student-to-teacher request
- [ ] Break-out rooms
- [ ] Interactive quizzes
- [ ] Hand gesture recognition during class
- [ ] Multi-language support
- [ ] ASL → English live caption

---

## 📝 Summary

**Current Status**: ✅ All analysis complete, ready to implement

**Total Development Time**: 60-90 minutes

**Files to Create**: 5 new files (~490 lines)

**Files to Modify**: 2 files (~150 lines additions)

**Breaking Changes**: NONE - all existing code stays unchanged

**Deployment Ready**: YES - can deploy same day

---

## ✋ Next Step

**Review the detailed plans:**
1. `CLASSROOM_IMPLEMENTATION_PLAN.md` - Full technical spec
2. `CLASSROOM_PLAN_VISUAL_SUMMARY.md` - Visual diagrams

**Questions?** Ask before I start implementing!

Ready to begin Phase 1? 🚀
