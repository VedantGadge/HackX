# 🎬 YouTube Caption Capture Fix Guide

## Problem Identified
The browser extension was **not detecting YouTube captions** due to:
1. **Outdated CSS selectors** - YouTube's DOM structure changed
2. **No fallback mechanisms** - No backup detection if selectors fail
3. **Mutation observer only** - Missing captions if events weren't fired correctly

## Solution Implemented

### ✅ What's Fixed
The `content.js` has been updated with:

1. **Multiple Caption Selectors** (in priority order):
   ```
   .captions-text              (Old/Legacy YouTube)
   .ytp-caption-segment        (Modern YouTube captions) ⭐ PRIMARY
   .ytp-caption                (Alternative modern selector)
   [aria-label*="caption"]     (Accessible elements)
   .a-text[jsname]             (Google's JavaScript framework)
   ```

2. **Smart Caption Extraction** (`extractCaptionText()` function):
   - Tries multiple DOM query methods
   - Scans caption windows
   - Searches near the video player
   - Filters out noise (very long text)

3. **Dual Detection Methods**:
   - **Primary**: MutationObserver (detects DOM changes in real-time)
   - **Backup**: Polling every 1 second (catches missed mutations)
   - **Fallback**: 500ms polling if no caption containers found

4. **Better State Tracking**:
   - Added `captureEnabled` flag for reliable capture control
   - Proper cleanup of observers and pollers on stop
   - More detailed console logging

## How to Deploy

### Step 1: Reload the Extension
```
1. Go to chrome://extensions
2. Find "Intellify" extension
3. Click the 🔄 Reload button
```

### Step 2: Test on YouTube
```
1. Go to youtube.com
2. Open any video WITH captions enabled (CC button visible)
3. Click extension icon → Verify Backend URL: http://127.0.0.1:5000
4. Click "Start Caption Capture"
5. Watch the DevTools Console (F12 → Console tab)
```

## Debugging Checklist

### Test Case 1: Caption Detection
**What to do:**
1. Enable captions (CC button) on a YouTube video
2. Click extension icon → "Start Caption Capture"
3. Watch console for logs

**Expected output:**
```
🎬 Starting caption capture...
🔍 Trying selector ".captions-text": found 0 element(s)
🔍 Trying selector ".ytp-caption-segment": found 2 element(s)
✅ Using selector: .ytp-caption-segment
📌 Observing container 1/2
📌 Observing container 2/2
✅ Caption capture started - watching for caption changes on ".ytp-caption-segment"
💡 Backup polling enabled every 1 second
```

**If not found:** Check next section

### Test Case 2: If Captions Still Not Detected
**What to do:**
1. Open DevTools (F12)
2. Go to Inspector tab
3. Click the picker tool (top-left corner)
4. Click on the caption text on YouTube player
5. Note the `class` or `id` of the element

**Share with me:**
- The HTML element you see
- The class/id names
- Screenshot of the DOM

### Test Case 3: Caption Extraction
Once captions are detected, **check if text is being extracted:**

**Expected output when caption appears:**
```
📝 New caption detected: "We are going to college"
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
Caption text: "We are going to college"
Request time: 2:45:30 PM
📤 Sending to backend...
⏱️ Response time: 120ms
📊 Response status: 200 OK
✅ TOKENIZATION SUCCESS
   Mapped tokens: [we, go, college]
```

### Test Case 4: Backend Connection
**If you see "NETWORK ERROR":**

1. **Check backend is running:**
   ```powershell
   # In PowerShell
   curl http://127.0.0.1:5000/health
   # Should return: {"status":"ok"}
   ```

2. **If not running, start it:**
   ```powershell
   cd D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
   python app.py
   ```

### Test Case 5: Full End-to-End Flow

**Video to test with:**
```
Go to: https://www.youtube.com/watch?v=<any_id_with_captions>
Or try: Search "hello world" and pick a video with CC
```

**Steps:**
1. ✅ Captions visible (CC button on)
2. ✅ Extension loaded (check icon in toolbar)
3. ✅ Click "Start Caption Capture"
4. ✅ Play video or read caption aloud
5. ✅ Check console for "New caption detected"
6. ✅ Check Network tab for `/tokenize-text` request
7. ✅ Watch overlay video play

## Console Log Reference

| Log | Meaning | Action |
|-----|---------|--------|
| `🎬 Starting caption capture...` | Capture initializing | ✅ Good |
| `🔍 Trying selector "..."` | Checking for captions | ✅ Good |
| `✅ Using selector: ...` | Found captions! | ✅ Good |
| `⚠️ No caption containers found` | No captions on page | ❌ Enable CC |
| `✅ Fallback polling started` | Using polling method | ⚠️ Fallback mode |
| `📝 New caption detected` | Caption found! | ✅ Good |
| `❌ NETWORK ERROR` | Backend unreachable | ❌ Start backend |
| `✅ TOKENIZATION SUCCESS` | Backend processed it | ✅ Good |
| `Mapped tokens: [...]` | Videos to play | ✅ Good |
| `▶️ PLAYING VIDEO CLIP` | Video started | ✅ Good |

## Troubleshooting

### Problem: "Found 0 caption container(s)" but CC is enabled

**Solution:** YouTube's DOM changed again
1. Inspect the caption element (right-click → Inspect)
2. Look for the class name
3. Tell me the class/id you see
4. I'll add it to the selectors

### Problem: Captions detected but no backend response

**Check:**
1. Is backend running? `curl http://127.0.0.1:5000/health`
2. Check Network tab for `/tokenize-text` request
3. What's the HTTP status? (200, 404, 500, etc.)

### Problem: Backend responds but no videos play

**Likely cause:** Videos folder is empty

```powershell
# Check videos folder
Get-ChildItem D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\videos -Filter "*.mp4" | Select-Object Name | head -10
```

**If empty:** Add .mp4 files named as tokens (e.g., `we.mp4`, `go.mp4`)

### Problem: Random words don't have videos

**This is normal!** Not every word has a video.

**Check console output:**
```
Missing (no video): [are, to, you]
Available in videos/: 45 tokens
```

**Solution:** Either:
- Add videos for missing tokens: `are.mp4`, `to.mp4`, `you.mp4`
- Add synonyms in `app.py` to map to existing videos

## Performance Tips

- **Polling frequency:** Currently 1 second + 500ms fallback
- If CPU usage is high: Increase polling interval in code
- If captions are missed: Decrease polling interval

## Modified Files

```
chrome_extension/
  └── content.js  ✏️ UPDATED
      ├── Added captionPoller variable
      ├── Added captureEnabled flag
      ├── Updated startCaptureCaptions() with polling
      ├── Added extractCaptionText() function
      ├── Updated stopCaptureCaptions()
      └── Updated toggleCaptureCaptions()
```

## Next Steps

1. **Reload extension**: chrome://extensions → Reload Intellify
2. **Test on YouTube**: Try a video with captions
3. **Check console**: F12 → Console tab
4. **Share logs** if still not working

## Questions?

Check these files for more details:
- `TESTING.md` - Testing procedures
- `DEBUG_GUIDE.md` - Detailed debugging
- `API_CONTRACT.md` - Backend API spec
- `ARCHITECTURE.md` - System design

---

**Last Updated:** October 30, 2025
**Changes:** Multiple caption selectors + polling fallback + improved logging
