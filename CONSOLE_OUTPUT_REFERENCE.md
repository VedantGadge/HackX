# 📋 Console Output Reference - What to Expect

## Extension Startup (Page Load)

When you visit a YouTube page with the extension installed, you should see:

```javascript
✅ Intellify content script loaded
```

This confirms the extension's main script (content.js) has been injected into the YouTube page.

---

## Clicking "Start Caption Capture"

When you click the "Start Caption Capture" button in the extension popup:

### ✅ Expected (Good)
```javascript
🎬 Starting caption capture...
📊 Found 1 caption container(s)
   Observing container 1/1
✅ Caption capture started - watching for caption changes
```

**What it means**: The extension found the YouTube caption element and is now listening for changes.

### ❌ Unexpected (Problem)
```javascript
🎬 Starting caption capture...
📊 Found 0 caption container(s)
⚠️ No caption containers found with selector ".captions-text"
🔍 Trying alternative selectors...
   Trying ".ytp-caption-segment": found 0 element(s)
   Trying "[role="status"]": found 0 element(s)
   Trying ".captions": found 0 element(s)
   Trying "[aria-label*="caption"]": found 0 element(s)
💡 Make sure captions are ENABLED on the video (click CC button)
```

**What it means**: Captions aren't detected. Click the CC button on YouTube to enable them.

---

## When a Caption Appears

When YouTube updates the captions (either by playing video or manual caption change):

### ✅ Expected (Caption Detected)
```javascript
🔄 Caption unchanged (same as before), skipping...
🔄 Caption unchanged (same as before), skipping...
📝 New caption detected: "We are going to college"
```

**What it means**: Extension detected a NEW caption text that's different from before.

### The Tokenization Request

Immediately after detecting a caption:

```javascript
============================================================
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
Caption text: "We are going to college"
Request time: 2:45:30 PM
📤 Sending to backend...
⏱️ Response time: 120ms
📊 Response status: 200 OK
✅ TOKENIZATION SUCCESS
   Mapped tokens: [we, go, college]
   All tokens: [we, are, go, to, college]
   Missing (no video): [are, to]
   Available in videos_: 45 tokens
============================================================
```

**Line by line**:
- `🌐 TOKENIZATION REQUEST` - Starting a tokenization operation
- `Backend URL: http://127.0.0.1:5000` - Where the extension is sending the request
- `Caption text: "We are going to college"` - What was said/captioned
- `Request time: 2:45:30 PM` - When this occurred
- `📤 Sending to backend...` - Request is being sent (network call)
- `⏱️ Response time: 120ms` - Backend responded in 120 milliseconds (good if <500ms)
- `📊 Response status: 200 OK` - HTTP 200 = success
- `✅ TOKENIZATION SUCCESS` - Backend processed successfully
- `   Mapped tokens: [we, go, college]` - Words that have video files
- `   All tokens: [we, are, go, to, college]` - All words detected (including those without videos)
- `   Missing (no video): [are, to]` - Words without video files (will be skipped)
- `   Available in videos_: 45 tokens` - Total number of video files on server

### Queue Management

After tokenization succeeds:

```javascript
📊 Queue updated, total items: 3
```

**What it means**: 3 video clips have been added to the queue (for: we, go, college)

---

## Video Playback

When videos start playing from the queue:

### First Video
```javascript
▶️ PLAYING VIDEO CLIP
Token: we
URL: http://127.0.0.1:5000/token-video/we
Queue remaining: 2
⏱️ Video loaded and playing
```

**What it means**:
- `Token: we` - Playing the "we" video
- `URL: http://127.0.0.1:5000/token-video/we` - Where it's fetching from
- `Queue remaining: 2` - 2 more videos waiting after this
- Videos play until the `ended` event fires

### Video Finishes
```javascript
✅ Finished playing: we
▶️ PLAYING VIDEO CLIP
Token: go
URL: http://127.0.0.1:5000/token-video/go
Queue remaining: 1
⏱️ Video loaded and playing
```

**What it means**: First video finished, automatically starting the next one

### Queue Empties
```javascript
✅ Finished playing: college
✅ Queue empty - all videos played!
```

**What it means**: All videos have been played, queue is cleared.

---

## Error Scenarios

### ❌ Scenario 1: Backend Not Running

**Console output**:
```javascript
📝 New caption detected: "We are going"
============================================================
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
Caption text: "We are going"
Request time: 2:45:30 PM
📤 Sending to backend...
❌ NETWORK ERROR
Error type: TypeError
Error message: Failed to fetch
Attempted URL: http://127.0.0.1:5000/tokenize-text
============================================================
```

**What it means**: 
- Extension tried to reach backend but couldn't connect
- Backend server is NOT running

**Fix**:
```powershell
# In a new PowerShell window:
cd D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
python app.py
```

---

### ❌ Scenario 2: Wrong Backend URL

**Console output**:
```javascript
❌ NETWORK ERROR
Error type: TypeError
Error message: Failed to fetch
Attempted URL: http://192.168.1.100:5000/tokenize-text
```

**What it means**:
- Extension is trying to reach a different IP/port
- URL configuration is wrong

**Fix**:
1. Click Intellify extension icon
2. Check Backend URL field (should be `http://127.0.0.1:5000`)
3. Update if necessary

---

### ❌ Scenario 3: No Videos Available

**Console output**:
```javascript
✅ TOKENIZATION SUCCESS
   Mapped tokens: []
   All tokens: [we, are, go, to, college]
   Missing (no video): [we, are, go, to, college]
   Available in videos_: 0 tokens
============================================================

📊 Queue updated, total items: 0
✅ Queue empty - all videos played!
```

**What it means**:
- Backend found 0 video files in videos/ folder
- All tokens are marked as "missing"
- Queue is empty (nothing to play)

**Fix**:
1. Add .mp4 files to `videos/` folder
2. Name them by token (e.g., `we.mp4`, `go.mp4`)
3. Restart backend with `python app.py`

---

### ❌ Scenario 4: Backend Returns Error

**Console output**:
```javascript
❌ TOKENIZATION FAILED - HTTP 500
Status Text: Internal Server Error
Response: Error: LLM not available
============================================================
```

**What it means**:
- Backend encountered an error processing the request
- HTTP 500 = Server error

**Fix**:
1. Check backend terminal for error details
2. Review backend logs
3. Restart backend: `python app.py`

---

## Filter Logs in Console

To focus on specific operations, use Console filters:

1. **In DevTools Console**, click the filter icon 🔍
2. **Type to filter**:
   - `TOKENIZATION` - Show only tokenization operations
   - `PLAYING` - Show only video playback
   - `ERROR` - Show only errors
   - `Token:` - Show specific token playback

**Example filtered output** (showing only PLAYING):
```javascript
▶️ PLAYING VIDEO CLIP
Token: we

✅ Finished playing: we
▶️ PLAYING VIDEO CLIP
Token: go

✅ Finished playing: go
▶️ PLAYING VIDEO CLIP
Token: college
```

---

## Full Successful Session

Here's what a complete successful session looks like:

```javascript
✅ Intellify content script loaded

🎬 Starting caption capture...
📊 Found 1 caption container(s)
   Observing container 1/1
✅ Caption capture started - watching for caption changes

📝 New caption detected: "We are going to college"
============================================================
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
Caption text: "We are going to college"
Request time: 2:45:30 PM
📤 Sending to backend...
⏱️ Response time: 120ms
📊 Response status: 200 OK
✅ TOKENIZATION SUCCESS
   Mapped tokens: [we, go, college]
   All tokens: [we, are, go, to, college]
   Missing (no video): [are, to]
   Available in videos_: 45 tokens
============================================================

📊 Queue updated, total items: 3

▶️ PLAYING VIDEO CLIP
Token: we
URL: http://127.0.0.1:5000/token-video/we
Queue remaining: 2
⏱️ Video loaded and playing

✅ Finished playing: we
▶️ PLAYING VIDEO CLIP
Token: go
URL: http://127.0.0.1:5000/token-video/go
Queue remaining: 1
⏱️ Video loaded and playing

✅ Finished playing: go
▶️ PLAYING VIDEO CLIP
Token: college
URL: http://127.0.0.1:5000/token-video/college
Queue remaining: 0
⏱️ Video loaded and playing

✅ Finished playing: college
✅ Queue empty - all videos played!
```

---

## Log Emoji Key

| Emoji | Meaning |
|-------|---------|
| 🎬 | Setup/initialization |
| 📊 | Status/count information |
| 🌐 | Network/backend communication |
| 📤 | Sending data |
| ⏱️ | Timing information |
| ✅ | Success |
| ❌ | Error |
| ⚠️ | Warning |
| 📝 | Event/action |
| ▶️ | Playback action |
| 🔄 | Duplicate/skipped |
| 🔍 | Investigation/search |
| 💡 | Hint/suggestion |

---

## Debugging Tips

### Copy Full Logs
```javascript
// In console, you can right-click and "Save as" to save console output
// Or select all with Ctrl+A and copy with Ctrl+C
```

### Monitor Specific Events
Use CSS filter to focus on what you need:

- `New caption` - Only show when captions appear
- `PLAYING` - Only show video playback
- `ERROR` - Only show errors
- `Response time` - Only show backend timing

### Check Network Tab

For network-level debugging:

1. **F12** → **Network** tab
2. **Filter by "Fetch/XHR"**
3. **Look for**:
   - `POST /tokenize-text` requests
   - `GET /token-video/[token]` requests
   - Status should be 200 or 206

---

## Reading the Logs Flowchart

```
Does console show "content script loaded"?
    ├─ No → Extension not injected
    │   └─ Reload extension, refresh page
    │
    └─ Yes
        ↓
Does console show "Caption capture started"?
    ├─ No → You haven't clicked "Start" button
    │   └─ Click "Start Caption Capture"
    │
    └─ Yes
        ↓
Does console show "New caption detected"?
    ├─ No → Captions aren't changing
    │   └─ Enable CC, play video
    │
    └─ Yes
        ↓
Does console show "TOKENIZATION SUCCESS"?
    ├─ No → Backend error
    │   └─ Check backend logs, HTTP status
    │
    └─ Yes
        ↓
Does console show "Mapped tokens: [...]" with items?
    ├─ No → No video files available
    │   └─ Add .mp4 files to videos/ folder
    │
    └─ Yes
        ↓
Does console show "PLAYING VIDEO CLIP"?
    ├─ No → Video element issue
    │   └─ Check for JavaScript errors
    │
    └─ Yes
        ↓
✅ SUCCESS! Videos are playing!
```

---

## Quick Reference Table

| Log Output | Status | Action |
|-----------|--------|--------|
| `content script loaded` | ✅ | Normal, extension working |
| `Found 1 container` | ✅ | Captions detected |
| `Found 0 container` | ❌ | Enable CC button |
| `Caption capture started` | ✅ | Listening for changes |
| `New caption detected` | ✅ | Processing caption |
| `TOKENIZATION REQUEST` | ✅ | Sending to backend |
| `Response time: XXms` | ✅ | Backend responded |
| `TOKENIZATION SUCCESS` | ✅ | Got tokens back |
| `Mapped tokens: [...]` | ✅ | Has playable videos |
| `Mapped tokens: []` | ❌ | No video files |
| `NETWORK ERROR` | ❌ | Backend not running |
| `PLAYING VIDEO CLIP` | ✅ | Video is playing |
| `Queue empty` | ✅ | All videos played |

---

**Now you know exactly what to expect in the console!** 🎉

Use this guide to understand the logs and troubleshoot any issues.
