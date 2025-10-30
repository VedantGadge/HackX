# Intellify: Complete System Flowchart

## Data Flow: Speech → Sign Language Video

```
═══════════════════════════════════════════════════════════════════════
                         OPTION A: SPEECH INPUT
                      (Add Whisper or Google STT)
═══════════════════════════════════════════════════════════════════════

                          🎙️ SPEECH AUDIO
                              (MP3/WAV)
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ SPEECH-TO-TEXT (NEW)    │
                    │ ─────────────────────── │
                    │ • Whisper (offline)     │
                    │ • Google Cloud (online) │
                    │ • Web Speech API        │
                    └────────┬────────────────┘
                             │
                             ▼
                      "We are going to college"

═══════════════════════════════════════════════════════════════════════

                            OPTION B: TEXT INPUT
                         (Current - Fully Working)

                      "We are going to college"

═══════════════════════════════════════════════════════════════════════

                       📝 TEXT NORMALIZATION
                            ↓
                   • Lowercase: "we are going to college"
                   • Remove punctuation
                   • Strip whitespace
                             ↓
                    "we are going to college"

                       🤖 GLOSS GENERATION
                   (OpenAI GPT-4o-mini LLM)
                            ↓
                   Prompt: "Convert to ASL gloss"
                             ↓
                    Response: "WE GO COLLEGE"

                    🔄 TOKENIZATION & FILTERING
                            ↓
                   • Stemming: ["we", "go", "college"]
                   • Stopword removal
                   • Available video matching
                             ↓
                    Final tokens: ["we", "go", "college"]

═══════════════════════════════════════════════════════════════════════

                    🎬 VIDEO MAPPING & SELECTION

    Token: "we"          Token: "go"        Token: "college"
       │                    │                   │
       └──────────────────────────────────────────┘
              (All tokens map to available videos)
       │                    │                   │
       ▼                    ▼                   ▼
   we.mp4              go.mp4             college.mp4
   120 frames          145 frames          155 frames
   25 FPS              25 FPS              25 FPS
   640x480             640x480             640x480

═══════════════════════════════════════════════════════════════════════

              🎞️ VIDEO COMPOSITION & CONCATENATION

    Input Files:
    ├── we.mp4      (frames 0-119)
    ├── go.mp4      (frames 120-264)
    └── college.mp4 (frames 265-419)
                ↓
    Process:
    ├── Read we.mp4:      120 frames
    ├── Write to output
    ├── Read go.mp4:      145 frames
    ├── Write to output
    ├── Read college.mp4: 155 frames
    ├── Write to output
    ├── Close writer
    └── Return output file
                ↓
    Output: reverse_20251030_150230_123456.mp4
    ├── Total frames: 420
    ├── Duration: 16.8 seconds (at 25 FPS)
    ├── Resolution: 640x480
    ├── Codec: H.264 (avc1)
    └── Size: ~5-10 MB

═══════════════════════════════════════════════════════════════════════

              🌐 WEB SERVER RESPONSE

    JSON Response:
    {
      "video_url": "/outputs/reverse_20251030_150230_123456.mp4",
      "file": "reverse_20251030_150230_123456.mp4",
      "tokens": ["we", "go", "college"],
      "meta": {
        "fps": 25.0,
        "width": 640,
        "height": 480,
        "frames": 420,
        "duration_seconds": 16.8,
        "missing": [],
        "codec": "avc1"
      }
    }

═══════════════════════════════════════════════════════════════════════

              📺 BROWSER PLAYBACK

    HTML:
    <video src="/outputs/reverse_20251030_150230_123456.mp4" 
           controls width="640" height="480"></video>

    Result:
    ┌─────────────────────────────────────┐
    │ 🎬 Sign Language Demonstration      │
    │                                     │
    │  [Video plays with hand gestures]   │
    │  WE → GO → COLLEGE                  │
    │                                     │
    │  [▶] [░░░░░░░░░░░░░░░░░] [16.8s]  │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
```

---

## API Request/Response Cycle

```
╔════════════════════════════════════════════════════════════════════╗
║                        CLIENT (Browser/API)                        ║
╚════════════════════════════════════════════════════════════════════╝
                              │
                              │ POST /reverse-translate-video
                              │ Content-Type: application/json
                              │
                              ▼
                    ┌──────────────────────┐
                    │ REQUEST BODY         │
                    ├──────────────────────┤
                    │ {                    │
                    │   "text": "We go     │
                    │    college",         │
                    │   "glossTokens": null│
                    │ }                    │
                    └─────────┬────────────┘
                              │
                              ▼
╔════════════════════════════════════════════════════════════════════╗
║                   SERVER (Flask app.py:5000)                       ║
║                                                                    ║
║  @app.route('/reverse-translate-video', methods=['POST'])          ║
║  def reverse_translate_video():                                    ║
║                                                                    ║
║  ├─ 1. Parse JSON payload                                          ║
║  ├─ 2. Extract text or glossTokens                                 ║
║  ├─ 3. IF text → call LLM (revtrans.sentence_to_gloss_tokens)     ║
║  │     ├─ Import function                                          ║
║  │     ├─ Get available video tokens                               ║
║  │     ├─ Call OpenAI GPT-4o-mini                                  ║
║  │     └─ Filter tokens against available clips                    ║
║  ├─ 4. Generate gloss_tokens list                                  ║
║  ├─ 5. Call compose_video_from_gloss(gloss_tokens)                │
║  │     ├─ Map tokens to video files                                ║
║  │     ├─ Extract video metadata                                   ║
║  │     ├─ Create VideoWriter (H.264)                               ║
║  │     ├─ Stream frames from each video                            ║
║  │     └─ Return filename + metadata                               ║
║  ├─ 6. Build response JSON                                         ║
║  └─ 7. Return 200 OK with JSON                                     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
                              │
                              │ HTTP 200 OK
                              │ Content-Type: application/json
                              │
                              ▼
                    ┌──────────────────────────────┐
                    │ RESPONSE BODY                │
                    ├──────────────────────────────┤
                    │ {                            │
                    │   "video_url":               │
                    │   "/outputs/reverse_20....", │
                    │   "file": "reverse_20....",  │
                    │   "tokens":                  │
                    │   ["we", "go", "college"],   │
                    │   "meta": {                  │
                    │     "fps": 25.0,             │
                    │     "width": 640,            │
                    │     "height": 480,           │
                    │     "frames": 420,           │
                    │     "missing": [],           │
                    │     "codec": "avc1"          │
                    │   }                          │
                    │ }                            │
                    └────────┬─────────────────────┘
                              │
                              ▼
╔════════════════════════════════════════════════════════════════════╗
║                   CLIENT RECEIVES RESPONSE                         ║
╚════════════════════════════════════════════════════════════════════╝
                              │
                              │ Extract video_url
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ GET /outputs/reverse... │
                    │ (with HTTP Range       │
                    │  support for streaming)│
                    └────────┬────────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ Video File (.mp4)       │
                    │ H.264 codec             │
                    │ 640x480 @ 25 FPS        │
                    │ 16.8 seconds            │
                    └────────┬────────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │ Browser HTML5 Video     │
                    │ <video controls></video>│
                    │ User plays video        │
                    └─────────────────────────┘
```

---

## Caching Strategy

```
┌────────────────────────────────────────────────────────────┐
│                   TEXT INPUT                               │
│           "We are going to college"                        │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ NORMALIZE TEXT       │
          │ (lowercase, trim)    │
          └────────┬─────────────┘
                   │
                   ▼ "we are going to college"
          ┌──────────────────────┐
          │ SHA1 HASH            │
          │ SHA1(text)           │
          └────────┬─────────────┘
                   │
                   ▼ "7f3e8c2a1b4c5d6e7f8g9h0i1j2k3l4m"
          ┌──────────────────────────────────┐
          │ CACHE FILENAME                   │
          │ seg_7f3e8c2a1b4c5d...mp4        │
          └────────┬────────────────────────┘
                   │
                   ├─── CACHE HIT ────────┐
                   │ File exists & non-empty  │
                   ▼                       ▼
        RETURN CACHED          COMPOSE & CACHE
        (instant)              (first time)
                   │                       │
                   └──────────┬────────────┘
                              │
                              ▼
                   /outputs/seg_7f3e8c2a.mp4

BENEFIT: Same text → Same file → Instant 2nd+ requests
EXAMPLE:
  Request 1: "We go college" → 5 seconds (compose)
  Request 2: "We go college" → 100ms (cache hit)
  Request 3: "We go college" → 100ms (cache hit)
```

---

## Error Handling Flow

```
REQUEST → Validate JSON
           │
           ├─ Missing "text" & "glossTokens"?
           │  ↓ Return 400: "Invalid payload"
           │
           └─ Valid JSON?
              │
              ├─ NO → Return 400: "Parse error"
              │
              └─ YES
                 │
                 ▼ Get LLM tokens
                 │
                 ├─ OpenAI API available?
                 │  │
                 │  ├─ NO
                 │  │  └─ Use fallback tokenizer
                 │  │
                 │  └─ YES
                 │     ├─ Call LLM
                 │     ├─ API Error?
                 │     │  ├─ YES → Log error, use fallback
                 │     │  └─ NO → Get tokens
                 │     │
                 │     └─ Any tokens returned?
                 │        ├─ NO → Return 400: "No tokens"
                 │        └─ YES → Continue
                 │
                 ▼ Map tokens to videos
                 │
                 ├─ All tokens have videos?
                 │  │
                 │  ├─ NO → Log warnings (missing tokens)
                 │  │     but continue with available
                 │  │
                 │  └─ YES → Continue
                 │
                 ├─ Any videos found?
                 │  │
                 │  ├─ NO → Return 404: "No clips found"
                 │  │
                 │  └─ YES → Continue
                 │
                 ▼ Compose video
                 │
                 ├─ VideoWriter failed?
                 │  └─ Return 500: "Codec error"
                 │
                 ├─ No frames written?
                 │  └─ Return 500: "Empty output"
                 │
                 └─ Success?
                    └─ Return 200 OK + JSON

RESPONSE:
┌─ 200 OK ────────→ Success, video ready
├─ 400 Bad Request → Invalid input
├─ 404 Not Found ──→ No matching videos
└─ 500 Server Error → Processing failed
```

---

## Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    INTELLIFY SYSTEM ARCHITECTURE                │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CLIENT LAYER                                                   │
│  ├─ Web UI (index.html)                                          │
│  │  ├─ Text input form                                          │
│  │  ├─ Video player                                             │
│  │  └─ results display                                          │
│  │                                                               │
│  └─ API Clients (curl, fetch, requests)                         │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FLASK SERVER (app.py)                                          │
│  ├─ Route Handlers                                              │
│  │  ├─ /reverse-translate-video                                │
│  │  ├─ /reverse-translate-segment                              │
│  │  ├─ /reverse-translate-transcript                           │
│  │  ├─ /infer-frame                                            │
│  │  ├─ /infer-letter                                           │
│  │  └─ /outputs/<filename>                                     │
│  │                                                               │
│  ├─ PROCESSING MODULES                                          │
│  │  ├─ normalize_text()                                         │
│  │  ├─ _text_to_gloss_tokens()                                 │
│  │  ├─ compose_video_from_gloss()                              │
│  │  ├─ _compose_segment_from_text_cached()                     │
│  │  └─ run_inference_on_frame()                                │
│  │                                                               │
│  └─ EXTERNAL INTEGRATIONS                                       │
│     └─ revtrans.py (LLM module)                                │
│        ├─ text_to_gloss()                                      │
│        ├─ gloss_to_english_llm()                               │
│        └─ sentence_to_gloss_tokens()                           │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DATA LAYER                                                     │
│  ├─ Video Library (videos/)                                     │
│  │  ├─ 800+ MP4 video clips                                    │
│  │  ├─ organized by token name                                 │
│  │  └─ standardized H.264 format                               │
│  │                                                               │
│  ├─ Model Files (pretrained/)                                  │
│  │  ├─ gesture_model.pkl                                       │
│  │  └─ letter_model.pkl                                        │
│  │                                                               │
│  ├─ Output Directory (outputs/)                                │
│  │  └─ Generated MP4 videos                                    │
│  │     ├─ reverse_YYYYMMDD_HHMMSS.mp4 (timestamped)         │
│  │     └─ seg_<hash>.mp4 (cached segments)                    │
│  │                                                               │
│  └─ External Services                                           │
│     └─ OpenAI API                                              │
│        ├─ GPT-4o-mini model                                    │
│        └─ Text-to-gloss conversion                             │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  UTILITY MODULES                                                │
│  ├─ utils/logger.py        (logging)                           │
│  ├─ utils/setup.py         (model setup)                       │
│  ├─ utils/boxes.py         (bbox utilities)                    │
│  └─ utils/rich_handlers.py (formatting)                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Token-to-Video Mapping Example

```
INPUT SENTENCE: "I am happy to be a teacher"

STEP 1: Normalize
  "i am happy to be a teacher"

STEP 2: LLM Gloss Generation
  Prompt: Convert to ASL gloss
  Response: "I HAPPY TEACHER"

STEP 3: Tokenize
  ["I", "HAPPY", "TEACHER"]
  ↓ (to lowercase)
  ["i", "happy", "teacher"]

STEP 4: Check Available Videos
  Available in videos/:
  ├─ i.mp4 ✓
  ├─ happy.mp4 ✓
  ├─ teacher.mp4 ✓
  └─ All found!

STEP 5: Build File List
  [
    "videos/i.mp4",
    "videos/happy.mp4",
    "videos/teacher.mp4"
  ]

STEP 6: Extract Metadata
  i.mp4       : 120 frames @ 25 FPS, 640×480
  happy.mp4   : 150 frames @ 25 FPS, 640×480
  teacher.mp4 : 180 frames @ 25 FPS, 640×480

STEP 7: Concatenate Frames
  Frame 0-119:    [i.mp4 content]
  Frame 120-269:  [happy.mp4 content]
  Frame 270-449:  [teacher.mp4 content]
  
  Total: 450 frames @ 25 FPS = 18 seconds

STEP 8: Encode Output
  Output file: reverse_20251030_150230_123456.mp4
  ├─ Codec: H.264 (avc1)
  ├─ Resolution: 640×480
  ├─ FPS: 25
  ├─ Duration: 18 seconds
  └─ Size: ~8 MB

STEP 9: Return to User
  {
    "video_url": "/outputs/reverse_20251030_150230_123456.mp4",
    "tokens": ["i", "happy", "teacher"],
    "meta": {
      "frames": 450,
      "duration_seconds": 18.0,
      "fps": 25.0,
      "codec": "avc1"
    }
  }
```

---

## System Capabilities Matrix

```
┌────────────────────┬─────────────┬──────────────┬──────────────────┐
│ Feature            │ Status      │ Performance  │ Notes            │
├────────────────────┼─────────────┼──────────────┼──────────────────┤
│ Text Input         │ ✓ Complete  │ <100ms       │ Immediate        │
│ LLM Gloss Gen      │ ✓ Complete  │ 1-2 sec      │ GPT-4o-mini      │
│ Fallback Tokenize  │ ✓ Complete  │ <50ms        │ Always available │
│ Video Library      │ ✓ Excellent │ -            │ 800+ clips       │
│ Clip Selection     │ ✓ Complete  │ <10ms        │ Fast lookup      │
│ Video Composition  │ ✓ Complete  │ 2-5 sec      │ OpenCV           │
│ H.264 Encoding     │ ✓ Complete  │ Built-in     │ Browser compat   │
│ Segment Caching    │ ✓ Complete  │ <100ms       │ SHA1 hashing     │
│ Batch Processing   │ ✓ Complete  │ Sequential   │ 20-30s for 5     │
│ HTTP Range Support │ ✓ Complete  │ Streaming    │ Video streaming  │
│ CORS Support       │ ✓ Complete  │ -            │ Cross-origin OK  │
│ API Documentation  │ ✓ Complete  │ -            │ Full endpoints   │
│ Gesture Recognition│ ✓ Complete  │ <50ms        │ MediaPipe        │
│ Letter Recognition │ ✓ Complete  │ <50ms        │ Separate model   │
│ Speech-to-Text     │ ⚠ Missing   │ -            │ Add Whisper/GST  │
│ Audio Output       │ ⚠ Missing   │ -            │ Optional feature │
│ Smooth Transitions │ ⚠ Missing   │ -            │ Direct concat OK │
└────────────────────┴─────────────┴──────────────┴──────────────────┘

Legend:
✓ = Implemented & working
⚠ = Partially available or optional
✗ = Not implemented
```

---

## Deployment Architecture

```
                        INTERNET
                            │
                            ▼
                    ┌─────────────────┐
                    │   DNS / LB      │
                    │   example.com   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────────────────┐
                    │    NGINX (Reverse Proxy)    │
                    │  • HTTPS termination        │
                    │  • Static file serving      │
                    │  • Load balancing (if multi)│
                    └────────┬────────────────────┘
                             │
         ┌─────────────┬─────┴─────┬─────────────┐
         │             │           │             │
         ▼             ▼           ▼             ▼
    ┌─────────┐   ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Flask   │   │ Flask   │ │ Flask   │ │ Flask   │
    │ :5000   │   │ :5001   │ │ :5002   │ │ :5003   │
    │ (app.py)│   │ (app.py)│ │ (app.py)│ │ (app.py)│
    └────┬────┘   └────┬────┘ └────┬────┘ └────┬────┘
         │             │           │            │
         └─────────────┼───────────┼────────────┘
                       │           │
                       ▼           ▼
              ┌─────────────────────────────┐
              │  SHARED STORAGE             │
              │  ├─ /videos (800+ clips)    │
              │  ├─ /outputs (generated)    │
              │  ├─ /models (PKL files)     │
              │  └─ /logs                   │
              └─────────────────────────────┘
                       │
                       ▼
              ┌─────────────────────────────┐
              │  CACHE LAYER (Optional)     │
              │  ├─ Redis/Memcached         │
              │  ├─ Segment caching         │
              │  └─ LLM result caching      │
              └─────────────────────────────┘
                       │
                       ▼
              ┌─────────────────────────────┐
              │  EXTERNAL SERVICES          │
              │  ├─ OpenAI API              │
              │  │  └─ GPT-4o-mini          │
              │  └─ (Optional: GCP/Azure)   │
              └─────────────────────────────┘
```

---

## Next Steps

1. **Add Speech Input** (Choose one):
   - Whisper (local, offline)
   - Google Cloud Speech-to-Text (cloud, accurate)
   - Web Speech API (browser-based)

2. **Enhance Output**:
   - Add background music
   - Smooth transitions between clips
   - Audio sync with original speech

3. **Production Deployment**:
   - Docker containerization
   - Kubernetes orchestration
   - CDN for video delivery
   - Database for results logging

4. **Advanced Features**:
   - Real-time continuous transcription
   - Video effects/filters
   - Multi-language support
   - Custom sign vocabularies

**Status: READY FOR INTEGRATION! ✓**
