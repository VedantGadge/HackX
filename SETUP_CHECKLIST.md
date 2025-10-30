# ✅ Project Setup Checklist - Ready to Implement

## Current Status

### ✅ What You Already Have

- **OpenAI API Key**: ✅ Configured in `.env`
  - Used for: GPT-4o-mini (text → gloss conversion)
  - Used for: Whisper (speech-to-text)

- **Project Structure**: ✅ Complete
  - Flask app with existing routes
  - Video library (800+ clips)
  - ML models (gesture, letter recognition)
  - HTML templates

- **Core Functionality**: ✅ Working
  - `revtrans.py` → Text to gloss conversion
  - `app.py` → Video composition from gloss tokens
  - `/reverse-translate-video` endpoint → Already functional

---

## Pre-Implementation Checklist

### 1. Dependencies Check

**Currently installed (verify):**
```bash
pip list | grep -i "flask\|torch\|opencv\|mediapipe"
```

**Will be added:**
```bash
flask-socketio==5.3.4      # For WebSocket support
python-socketio==5.10.0    # WebSocket server
python-engineio==4.7.1     # WebSocket transport layer
```

### 2. Environment Variables

**Verify `.env` has:**
```
✅ OPENAI_API_KEY=sk-proj-...
```

**If using local Whisper (optional later):**
```
# Don't add yet, only if you want local speech recognition
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
```

### 3. Project Structure

**Current:**
```
✅ app.py (1028 lines)
✅ revtrans.py (166 lines)
✅ model.py (141 lines)
✅ templates/ (4 HTML files)
✅ static/ (CSS + JS)
✅ videos/ (800+ MP4 clips)
✅ pretrained/ (ML models)
```

**Will add:**
```
📝 templates/classroom_home.html   (NEW - 20 lines)
📝 templates/teacher.html          (NEW - 150 lines)
📝 templates/student.html          (NEW - 120 lines)
📝 static/classroom.css            (NEW - 200 lines)
📝 requirements.txt                (MODIFY - add 3 packages)
```

---

## Ready to Start Implementation? ✅

### Implementation Phases (Simplified)

**Phase 1: Add WebSocket Support (5-10 min)**
```python
# In app.py, add imports
from flask_socketio import SocketIO, emit, join_room, leave_room

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory session storage
active_classrooms = {}
```

**Phase 2: Create Routes (5 min)**
```python
@app.route('/classroom')
@app.route('/teacher')
@app.route('/student')
```

**Phase 3: Add Speech Helper (3-5 min)**
```python
def transcribe_audio(audio_base64):
    """Convert base64 audio to text using Whisper"""
    # Your implementation here
```

**Phase 4: WebSocket Event Handlers (10-15 min)**
```python
@socketio.on('teacher_join')
@socketio.on('student_join')
@socketio.on('send_speech')
@socketio.on('disconnect')
```

**Phase 5-8: HTML/CSS/Testing (45 min)**
- Create UI templates
- Add styling
- Test end-to-end

---

## What Gets REUSED (No Changes)

✅ Your existing functions will be reused as-is:

| Function | File | Usage |
|----------|------|-------|
| `sentence_to_gloss_tokens()` | revtrans.py | Convert text → gloss |
| `compose_video_from_gloss()` | app.py | Stitch gloss tokens → MP4 |
| `_list_available_video_tokens()` | app.py | Get available clips |
| Video library | /videos/ | MP4 source clips |
| ML models | /pretrained/ | (For frame/letter detection) |

---

## What Gets ADDED (New Code)

✅ Only these new components:

| Component | Type | Lines |
|-----------|------|-------|
| SocketIO initialization | Python | 3-5 |
| `/classroom` route | Python | 5 |
| `/teacher` route | Python | 3 |
| `/student` route | Python | 3 |
| `transcribe_audio()` | Python | 20-30 |
| WebSocket event handlers | Python | 80-100 |
| teacher.html | HTML/JS | 150 |
| student.html | HTML/JS | 120 |
| classroom_home.html | HTML | 20 |
| classroom.css | CSS | 200 |
| **TOTAL** | | **~510-580 lines** |

---

## Breaking Changes

### ✅ NONE

**All existing routes stay exactly the same:**
- `/` (index)
- `/learn` (learn page)
- `/reverse-translate-video` (existing API)
- `/reverse-translate-segment`
- `/infer-frame`
- `/infer-letter`
- `/model-status`
- `/outputs/<filename>`

**No changes to:**
- Database (already using in-memory only)
- ML models
- Video library structure
- OpenAI integration
- Existing HTML/CSS/JS

---

## Quick Start Command Sequence

When ready, here's what we'll execute:

```bash
# 1. Install new packages
pip install flask-socketio python-socketio python-engineio

# 2. Create new HTML files
# (I'll provide templates)

# 3. Create CSS file
# (I'll provide styles)

# 4. Modify app.py
# (I'll provide exact code additions)

# 5. Test locally
python app.py
# Open 3 browser windows to test

# 6. Deploy
git add .
git commit -m "Add classroom feature with WebSocket support"
git push origin master
```

---

## API Cost Estimate (Monthly)

**Using your OpenAI API key:**

| Service | Usage | Cost |
|---------|-------|------|
| GPT-4o-mini (text→gloss) | ~1 call per utterance | ~$0.001-0.005 per utterance |
| Whisper (speech→text) | ~1 call per utterance | ~$0.02 per minute of audio |
| | 100 utterances/hour | ~$2-5/hour of classroom |

**Example:** 1-hour classroom = ~$5-10 in API costs

(This is very cheap for the functionality!)

---

## Questions to Confirm

Before I start implementing Phase 1:

1. **Ready to proceed?** ✅
2. **Use OpenAI Whisper?** (current plan - $0.02/min)
   - OR local Whisper? (free, offline)
3. **Match existing dark theme?** (for UI)
4. **Want to deploy immediately after?** (Heroku/AWS/local)

---

## Next Steps

### Immediate (Today)
- ✅ Review the 4 planning documents:
  - `PLAN_SUMMARY.md` (executive overview)
  - `CLASSROOM_IMPLEMENTATION_PLAN.md` (detailed spec)
  - `CLASSROOM_PLAN_VISUAL_SUMMARY.md` (visual diagrams)
  - `CLASSROOM_QUICK_REFERENCE.md` (checklist)

### Phase 1 (When Ready - 5-10 min)
- Modify `app.py` to add SocketIO
- Install 3 new packages
- Create in-memory session storage

### Phase 2-4 (10-30 min)
- Add routes and WebSocket handlers
- Add speech transcription helper
- Core logic complete

### Phase 5-8 (30-45 min)
- Create HTML templates
- Add CSS styling
- Test and debug

### Deployment (10-20 min)
- Push to GitHub
- Deploy to cloud
- Test with real users

---

## Support Resources

All 3 planning documents include:
- ✅ Step-by-step implementation guide
- ✅ Code snippets (copy-paste ready)
- ✅ Architecture diagrams
- ✅ Testing checklist
- ✅ Debugging guide
- ✅ Performance metrics
- ✅ Future enhancement ideas

---

## Final Summary

| Aspect | Status |
|--------|--------|
| **OpenAI Key** | ✅ Ready |
| **Project Structure** | ✅ Ready |
| **Existing Code** | ✅ Reusable |
| **New Code** | ✅ Designed |
| **Testing Plan** | ✅ Created |
| **Documentation** | ✅ Complete |
| **Ready to Start** | ✅ YES |

---

## 🚀 Ready to Begin Phase 1?

**Answer these:**
1. Should I proceed with implementation?
2. Local Whisper or OpenAI Whisper for speech-to-text?
3. Any questions about the plan?

Once approved, we can have Phase 1 (WebSocket setup) done in under 10 minutes! ⚡
