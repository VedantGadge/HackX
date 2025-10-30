# 🔧 Debug Mode Activated - Enhanced Logging

## What Was Updated

I've added **comprehensive debugging logs** to help identify where issues are occurring. The logs will help you pinpoint whether the problem is:

1. **Caption Detection** (MutationObserver not catching captions)
2. **Backend Communication** (Can't reach the server)
3. **Token Mapping** (Tokens not matching video files)
4. **Video Playback** (Videos not playing from queue)

---

## Quick Start: How to Use Debug Logs

### 1. Open Browser Console
- Press **F12** on any YouTube page with the extension
- Click **Console** tab
- You'll see colorful logs with emojis 🎬🌐✅❌

### 2. Enable Caption Capture
- Click extension icon
- Click "Start Caption Capture" button
- You'll see logs immediately

### 3. Read the Logs
Logs are organized in sections with visual separators:

```
============================================================
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
Caption text: "We are going to college"
Request time: 2:45:30 PM
...
============================================================
```

---

## Debug Log Examples

### ✅ Everything Working Correctly

```
🎬 Starting caption capture...
📊 Found 1 caption container(s)
   Observing container 1/1
✅ Caption capture started - watching for caption changes

[When caption appears:]

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
   Available in videos/: 45 tokens
============================================================

▶️ PLAYING VIDEO CLIP
Token: we
URL: http://127.0.0.1:5000/token-video/we
Queue remaining: 2
⏱️ Video loaded and playing

✅ Finished playing: we
```

### ❌ Problem: Captions Not Detected

```
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

**Solution**: Enable captions first! Click the **CC** button on YouTube player.

### ❌ Problem: Backend Not Responding

```
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

**Solution**: Make sure `python app.py` is running in a terminal!

### ❌ Problem: No Videos for Tokens

```
✅ TOKENIZATION SUCCESS
   Mapped tokens: []
   All tokens: [we, are, go, to, college]
   Missing (no video): [we, are, go, to, college]
   Available in videos/: 0 tokens
============================================================
```

**Solution**: Add .mp4 files to the `videos/` folder (we.mp4, are.mp4, go.mp4, etc.)

---

## Key Debug Logs Explained

| Log | Emoji | What It Means | Action |
|-----|-------|--------------|--------|
| `Found X caption container(s)` | 📊 | Number of caption elements detected | X should be > 0 |
| `Caption capture started` | ✅ | MutationObserver ready to detect | Normal, you're good |
| `New caption detected` | 📝 | A caption appeared! | Normal process |
| `TOKENIZATION REQUEST` | 🌐 | Sending caption to backend | Normal process |
| `Response time: XXms` | ⏱️ | How fast backend responded | Normal |
| `TOKENIZATION SUCCESS` | ✅ | Backend returned tokens | Normal |
| `Mapped tokens: [...]` | ✅ | Tokens with available videos | More = better |
| `Missing (no video): [...]` | ⚠️ | Words without video clips | Expected for some words |
| `PLAYING VIDEO CLIP` | ▶️ | Video starting playback | Normal |
| `Finished playing` | ✅ | Video completed | Normal |
| `No caption containers found` | ❌ | Extension can't find caption text | Enable CC button |
| `NETWORK ERROR` | ❌ | Can't reach backend | Start `python app.py` |
| `No tokens could be mapped` | ⚠️ | No videos for these words | Add .mp4 files |

---

## Troubleshooting Workflow

### Step 1: Check Caption Detection
```
Expected Log: "📊 Found 1 caption container(s)"

If you see: "📊 Found 0 caption container(s)"
→ Enable CC button on YouTube
→ Refresh page
→ Try again
```

### Step 2: Check Backend Connection
```
Expected Log: "⏱️ Response time: XXms" followed by "✅ TOKENIZATION SUCCESS"

If you see: "❌ NETWORK ERROR"
→ Start backend: python app.py
→ Verify URL in extension popup
→ Try again
```

### Step 3: Check Token Availability
```
Expected Log: "   Mapped tokens: [we, go, college]"

If you see: "   Mapped tokens: []"
→ Add video files to videos/ folder
→ Restart backend
→ Try again
```

### Step 4: Check Video Playback
```
Expected Log: "▶️ PLAYING VIDEO CLIP" followed by "✅ Finished playing:"

If you don't see this:
→ Check videos/ folder has files
→ Check Network tab in DevTools (should see 200 responses)
→ Reload extension
```

---

## How to Share Debug Info

If you need help, copy these logs and share:

1. **Open Console** (F12 → Console)
2. **Select all logs** (Ctrl+A)
3. **Copy** (Ctrl+C)
4. **Paste** in your message

This helps identify the exact issue!

---

## Files Modified

✅ **`chrome_extension/content.js`**
- Added detailed logging to `startCaptureCaptions()`
- Added comprehensive logging to `processCaption()`
- Added step-by-step logging to `playNextFromQueue()`
- Each function now reports: what it's doing, where it's sending requests, what it's receiving back

✅ **`chrome_extension/DEBUG_GUIDE.md`** (NEW)
- Complete debugging guide with examples
- Step-by-step troubleshooting workflow
- Interpretation of all log messages
- Advanced debugging techniques

---

## Next Steps

1. **Reload the extension**
   - Go to `chrome://extensions`
   - Click the refresh button on Intellify

2. **Test on YouTube**
   - Go to youtube.com
   - Enable captions (CC button)
   - Click "Start Caption Capture"
   - Open Console (F12)
   - Watch the logs as videos play

3. **Share logs if still having issues**
   - Copy the console output
   - Tell me which log appears and where it stops

---

**Now you have visibility into exactly what the extension is doing!** 🔍🔧

Check the `DEBUG_GUIDE.md` file for more detailed troubleshooting steps.
