# 🐛 Intellify Extension - Debugging Guide

## How to View Debug Logs

### Step 1: Open DevTools
- Press **F12** on your keyboard, OR
- Right-click on the page → **Inspect**, OR
- Press **Ctrl+Shift+I** (Windows) or **Cmd+Option+I** (Mac)

### Step 2: Go to Console Tab
- Click the **Console** tab at the top of DevTools
- You should see colored logs starting with emojis

---

## Debug Output Examples

### ✅ Successful Caption Detection

You should see logs like:
```
🎬 Starting caption capture...
📊 Found 1 caption container(s)
   Observing container 1/1
✅ Caption capture started - watching for caption changes
```

### ✅ Caption Detected & Tokenized

```
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
   Available in videos/: 45 tokens

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
...
```

---

## Common Issues & How to Debug

### Issue 1: Captions Not Being Detected

**Symptom**: You see "Found 0 caption container(s)"

**Debugging Steps**:

1. **Check if captions are enabled**
   - Click the **CC** button in YouTube player
   - Confirm captions appear on screen

2. **Check for alternative selectors**
   - DevTools console will show:
   ```
   📊 Found 0 caption container(s)
   🔍 Trying alternative selectors...
      Trying ".ytp-caption-segment": found 2 element(s)
      Trying "[role="status"]": found 0 element(s)
      ...
   ```
   - If one of these shows `found X element(s)` where X > 0, YouTube's DOM has changed
   - **Report this** and we'll update the selector in content.js

3. **Manual DOM inspection**
   - Press **F12** → **Inspector** tab
   - Click the picker tool (top-left)
   - Click on caption text on YouTube
   - You'll see the actual element structure
   - Look for the class/ID name and tell us what it is

### Issue 2: Captions Detected But No Backend Response

**Symptom**: You see caption logged but no tokenization response

**Logs you'll see**:
```
📝 New caption detected: "We are going..."
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
📤 Sending to backend...
[No further logs - STUCK HERE]
```

**Debugging Steps**:

1. **Check if backend is running**
   ```powershell
   # In PowerShell, test:
   curl http://127.0.0.1:5000/health
   ```
   - Should show: `{"status":"ok"}`
   - If it fails, start the backend: `python app.py`

2. **Check Network Tab**
   - DevTools → **Network** tab
   - Play a video with captions
   - Look for a request to `/tokenize-text`
   - Click it to see:
     - **Status**: Should be 200 (not 404, 500, etc.)
     - **Request body**: Your caption text
     - **Response**: tokens array
   - If you don't see this request, the fetch isn't being sent

3. **Check Backend URL in Extension Popup**
   - Click Intellify extension icon
   - Verify Backend URL: `http://127.0.0.1:5000`
   - If it's different, update it and save

### Issue 3: Network Error (Failed to fetch)

**Symptom**: You see logs like:
```
❌ NETWORK ERROR
Error type: TypeError
Error message: Failed to fetch
Attempted URL: http://127.0.0.1:5000/tokenize-text
```

**Root Causes & Solutions**:

| Cause | Solution |
|-------|----------|
| Backend not running | Start it: `python app.py` in a terminal |
| Wrong IP/Port | Check popup, verify URL is correct |
| CORS issue | Ensure app.py has `CORS(app)` enabled |
| Firewall blocking | Check Windows Defender / Antivirus |
| Python error | Check terminal for error messages |

### Issue 4: Videos Not Playing (Empty Queue)

**Symptom**: Captions detected, tokenized, but no videos play

**Logs you'll see**:
```
✅ TOKENIZATION SUCCESS
   Mapped tokens: []
   All tokens: [we, are, go]
   Missing (no video): [we, are, go]
   Available in videos/: 0 tokens
```

**Debugging Steps**:

1. **Check videos/ folder has files**
   ```powershell
   # List all .mp4 files in videos folder
   Get-ChildItem D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\videos -Filter "*.mp4"
   ```
   - Should show files like: `we.mp4`, `go.mp4`, `college.mp4`

2. **If videos/ is empty**
   - You need to add .mp4 files there!
   - Files should be named: `<token>.mp4` (lowercase, no spaces)

3. **If videos/ has files but still showing 0 tokens**
   - Restart the backend: Stop and run `python app.py` again
   - Backend scans videos/ on startup

### Issue 5: Specific Video Not Playing (404 Error)

**Symptom**: Some words play, others don't

**Logs you'll see**:
```
📊 Found 1 caption container(s)
   Observing container 1/1
✅ TOKENIZATION SUCCESS
   Mapped tokens: [we, college]
   Missing (no video): [are, to]
```

**Debugging Steps**:

1. **This is expected!** Not every word has a video.

2. **To add missing tokens**:
   - Check the "Missing" list in the logs
   - Example: Missing `["are", "to"]`
   - For each missing token, either:
     - **Add a video**: Create `are.mp4`, `to.mp4` in videos/ folder
     - **Add a synonym**: Update the synonym map in app.py so "are" → "be" (if be.mp4 exists)

3. **Check if token-video endpoint is working**:
   ```powershell
   # Test if backend can serve a video
   curl -I http://127.0.0.1:5000/token-video/we
   ```
   - Should show: `HTTP/1.1 200 OK` or `206 Partial Content`
   - If `404 Not Found`: video file missing from videos/ folder

---

## Step-by-Step Debug Checklist

When debugging, follow this order:

```
┌─────────────────────────────────────────┐
│ 1. Captions appearing on YouTube?       │
│    No → Enable CC button                │
│    Yes → Continue                       │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ 2. "Caption capture started" in console?│
│    No → Click "Start Caption Capture"   │
│    Yes → Continue                       │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ 3. "New caption detected" in console?   │
│    No → Check alternative selectors     │
│    Yes → Continue                       │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ 4. Backend response 200 OK?             │
│    No → Check backend is running        │
│    Yes → Continue                       │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ 5. Mapped tokens > 0?                   │
│    No → Add video files to videos/      │
│    Yes → Continue                       │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ 6. Videos playing in overlay?           │
│    Yes → ✅ SUCCESS!                    │
│    No → Check video element & playback  │
└─────────────────────────────────────────┘
```

---

## Log Interpretation Cheat Sheet

| Log Pattern | Meaning | Action |
|-------------|---------|--------|
| `🎬 Starting caption capture` | Observer being set up | ✅ Normal |
| `📊 Found 0 caption container(s)` | No captions detected | ❌ Enable CC button |
| `✅ Caption capture started` | Observer ready | ✅ Normal |
| `📝 New caption detected:` | Caption detected | ✅ Normal |
| `🌐 TOKENIZATION REQUEST` | Sending to backend | ✅ Normal |
| `⏱️ Response time: XXms` | Backend responded | ✅ Normal |
| `❌ TOKENIZATION FAILED` | Backend error | ❌ Check backend logs |
| `❌ NETWORK ERROR` | Can't reach backend | ❌ Start backend server |
| `⚠️ No tokens could be mapped` | No videos for tokens | ❌ Add .mp4 files |
| `▶️ PLAYING VIDEO CLIP` | Video starting | ✅ Normal |
| `✅ Finished playing:` | Video completed | ✅ Normal |
| `Queue empty` | All videos played | ✅ Normal |

---

## Advanced Debugging

### Modify Console Filters
You can filter logs in the Console:

1. DevTools → **Console** tab
2. Click the filter icon 🔍
3. Type to filter:
   - `TOKENIZATION` - show only tokenization logs
   - `PLAYING` - show only video playback
   - `ERROR` - show only errors

### Pause on Error
1. DevTools → **Sources** tab
2. Check "Pause on caught exceptions"
3. Logs with errors will pause execution (helpful for debugging)

### Monitor Network Requests
1. DevTools → **Network** tab
2. Filter by "Fetch/XHR"
3. Watch each request:
   - Green ✅ = 200 status (good)
   - Red ❌ = 404/500 status (bad)
   - Click request to see headers & response

### Check Extension Storage
1. DevTools → **Application** tab (or **Storage** in Firefox)
2. Left sidebar → **Local Storage** or **Chrome Storage**
3. Find the entry for the extension
4. Should see: `{"backendUrl": "http://127.0.0.1:5000"}`

---

## Getting Help

When reporting issues, please include:

1. **Browser Console Logs**: Copy/paste the logs you see
2. **Network Tab Screenshots**: Show the /tokenize-text request
3. **Steps to Reproduce**: Exactly what you did
4. **Videos folder status**: Do you have .mp4 files?
5. **Backend status**: Is `python app.py` running?

---

## Reset & Troubleshoot

### Full Extension Reset
1. Go to chrome://extensions
2. Remove the Intellify extension
3. Delete the chrome_extension folder cache (if any)
4. Reload the extension (Load unpacked again)
5. Try again

### Clear Browser Cache
1. DevTools → **Application** tab
2. Left sidebar → **Cache Storage**
3. Click "Clear" to remove all cached videos

### Restart Backend
```powershell
# Stop the backend (Ctrl+C if running)
# Then start fresh:
cd D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
python app.py
```

---

## Performance Tips

- **Large Queue**: If you queue too many videos, it may slow down
  - Solution: Click "Clear Queue" button to reset

- **Network Latency**: Backend taking >500ms to respond?
  - Solution: Check network speed, verify Flask server not overloaded

- **CPU Usage**: Extension using lots of CPU?
  - Solution: Stop caption capture when not needed (toggle off)

---

**Still stuck?** Check ARCHITECTURE.md for component details or API_CONTRACT.md for backend specs!
