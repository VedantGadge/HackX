# Intellify Extension ↔ Backend API Contract

## Overview
The Chrome extension communicates with the Flask backend via REST API calls. This document details the expected requests and responses.

## Endpoints Used

### 1. POST /tokenize-text
**Purpose**: Convert caption text into sign language tokens

**Request**:
```json
{
  "text": "We are going to college"
}
```

**Response** (200 OK):
```json
{
  "tokens": ["we", "go", "college"],
  "tokens_all": ["we", "are", "go", "to", "college"],
  "missing": ["are", "to"],
  "available": ["we", "are", "go", "college", "hello", "world", ...]
}
```

**Fields**:
- `tokens` (array): Mapped tokens with available videos (use for playback)
- `tokens_all` (array): All tokenized words (full gloss)
- `missing` (array): Tokens without corresponding video files
- `available` (array): All .mp4 files found in videos/ directory

**Error Response** (400 Bad Request):
```json
{
  "error": "Text is required"
}
```

**Usage in Extension**:
```javascript
const response = await fetch(`${backendUrl}/tokenize-text`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: "We are going to college" })
});
const data = await response.json();
console.log(data.tokens);  // ["we", "go", "college"]
```

---

### 2. GET /token-video/<token>
**Purpose**: Retrieve the MP4 video file for a specific token

**Request**:
```
GET http://127.0.0.1:5000/token-video/we
```

**Response** (200 OK or 206 Partial Content):
```
[Binary MP4 data]
Content-Type: video/mp4
Content-Length: 245123
```

**Error Response** (404 Not Found):
```json
{
  "error": "Video file not found: we.mp4"
}
```

**Usage in Extension**:
```javascript
const video = document.createElement('video');
video.src = `${backendUrl}/token-video/we`;
video.play();
```

**Notes**:
- Backend supports HTTP Range requests (206 Partial Content)
- Video files must be in `videos/` directory with `.mp4` extension
- Token names are lowercase and URL-encoded

---

### 3. GET /health (Optional)
**Purpose**: Check if backend server is running

**Request**:
```
GET http://127.0.0.1:5000/health
```

**Response** (200 OK):
```json
{
  "status": "ok"
}
```

**Usage in Extension**:
```javascript
const health = await fetch(`${backendUrl}/health`);
if (health.ok) console.log("Backend is running");
```

---

## Data Flow Diagram

```
YouTube Page (youtube.com)
         ↓
    [Caption Changes]
         ↓
 content.js Detects Caption
         ↓
    [MutationObserver]
         ↓
POST /tokenize-text
    text: "We are going"
         ↓
   Backend Tokenizes
  (LLM or heuristic)
         ↓
 Response with tokens:
  ["we", "go"]
         ↓
[Enqueue in Queue]
         ↓
playNextFromQueue()
    ↓        ↓
GET /token-video/we
   GET /token-video/go
         ↓
[Play Video Clips]
    sequentially
         ↓
   Update Caption Bar
  "Next: [empty]"
         ↓
   Wait for video.ended
   Advance to next token
```

---

## Response Status Codes

| Code | Scenario | Typical Cause |
|------|----------|--------------|
| 200 | Success | Normal response |
| 206 | Partial Content | HTTP Range request for video streaming |
| 400 | Bad Request | Missing required field (e.g., text parameter) |
| 404 | Not Found | Video file doesn't exist for token |
| 500 | Server Error | Backend exception (check server logs) |
| 503 | Service Unavailable | Backend not running or overloaded |

---

## Error Handling in Extension

**Current Implementation** (content.js):
```javascript
async function processCaption(text) {
    try {
        const resp = await fetch(`${backendUrl}/tokenize-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        if (!resp.ok) {
            console.error(`Backend error: ${resp.status}`);
            return;
        }
        
        const data = await resp.json();
        enqueueTokens(data.tokens);
        
    } catch (err) {
        console.error('Network error:', err);
    }
}
```

**Common Errors**:
1. **TypeError: Failed to fetch** → Backend not running or CORS issue
2. **404 Not Found** → Token doesn't have a video file (expected behavior, video skipped)
3. **500 Internal Server Error** → Check backend logs for exception
4. **TypeError: JSON.parse()** → Backend returned non-JSON response

---

## Backend Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-...  # Optional: enables LLM tokenization
DEBUG=True             # Optional: verbose logging
```

### Directory Structure
```
├── app.py              # Flask backend
├── videos/             # Token video files
│   ├── we.mp4
│   ├── go.mp4
│   ├── college.mp4
│   └── ...
├── models/             # ML models
│   ├── gesture_model.pkl
│   └── letter_model.pkl
└── outputs/            # Cached composed videos
    └── ...
```

### Starting Backend
```bash
# Start on default localhost:5000
python app.py

# Or specify host/port
python app.py --host 0.0.0.0 --port 5000
```

---

## Testing with curl (for debugging)

### Test tokenization:
```bash
curl -X POST http://127.0.0.1:5000/tokenize-text \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}'
```

### Test video retrieval:
```bash
curl -I http://127.0.0.1:5000/token-video/hello
```

### Test health:
```bash
curl http://127.0.0.1:5000/health
```

---

## Extension to Backend Communication Flow

### Startup
1. Extension popup loads
2. Popup reads backend URL from `chrome.storage.sync`
3. User inputs custom URL (if needed)
4. User clicks "Start Caption Capture"
5. Popup sends message to content.js

### Runtime
1. content.js initializes overlay on YouTube page
2. MutationObserver detects caption changes
3. For each caption:
   - POST `/tokenize-text` with caption text
   - Backend returns token array (filtered to available videos)
   - Extension enqueues tokens
4. playNextFromQueue() loop:
   - GET `/token-video/<token>` for each token
   - Set `<video>` element src to this URL
   - Play video
   - Wait for `ended` event
   - Advance to next token

### Shutdown
1. User clicks "Clear Queue" or toggles capture off
2. Observers disconnect
3. Queue cleared
4. Video element paused

---

## Backwards Compatibility

**Current Version**: 1.0.0  
**Backend Requirement**: Flask app.py with these endpoints:
- POST `/tokenize-text`
- GET `/token-video/<token>`

**Future Versions**:
- Will add version header to requests for API versioning
- Backend should respond with `X-API-Version: 1.0` header

---

## Rate Limiting & Throttling

**Current Implementation**: None (local network, assumed fast)

**Future Considerations**:
- Backend may implement rate limiting per IP
- Extension should implement exponential backoff on 429 (Too Many Requests)
- Consider debouncing caption changes (e.g., wait 500ms before tokenizing)

---

## Example Integration Workflow

**Scenario**: User watches YouTube video with captions enabled

```
Time  | User Action        | Extension Action         | Backend Action
------|-------------------|--------------------------|--------------------
0ms   | Clicks "Start"    | Enables MutationObserver | (idle)
100ms | Caption appears   | Detects "Hello world"   | (idle)
100ms | (same)            | POST /tokenize-text     | Tokenizes → ["hello"]
150ms | (same)            | GET /token-video/hello  | Returns hello.mp4
200ms | (same)            | Plays hello.mp4         | (idle)
800ms | hello.mp4 ends    | playNextFromQueue()     | (idle)
800ms | (same)            | Queue empty, wait       | (idle)
1200ms| Caption changes   | Detects "How are you"   | (idle)
1200ms| (same)            | POST /tokenize-text     | Tokenizes → ["how", "are"]
1250ms| (same)            | GET /token-video/how    | Returns how.mp4
1300ms| (same)            | Plays how.mp4           | (idle)
```

---

**API Version**: 1.0.0  
**Last Updated**: 2024
