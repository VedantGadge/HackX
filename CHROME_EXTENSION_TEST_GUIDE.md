# 🧪 Chrome Extension Testing Guide

## 📋 Overview
Test the **Intellify Chrome Extension** with your deployed production backend at `https://lamaq-signlink-hackx.hf.space`.

The extension captures YouTube captions in real-time and displays ASL sign language video translations in a floating overlay.

---

## 🚀 Quick Start

### Step 1: Load Extension in Chrome

1. **Open Chrome** and navigate to:
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode**:
   - Toggle the switch in the top-right corner

3. **Load Unpacked Extension**:
   - Click "Load unpacked"
   - Navigate to: `C:\Users\lamaq\OneDrive\Desktop\MUJ REPO\chrome_extension`
   - Click "Select Folder"

4. **Verify Installation**:
   - You should see "Intellify - Real-time Sign Language Translator" in your extensions list
   - Pin it to the toolbar (click the puzzle icon → pin Intellify)

---

### Step 2: Configure Production Backend

1. **Click the Intellify Extension Icon** (🤟) in your Chrome toolbar

2. **Set Backend URL**:
   - You'll see a field labeled "Backend URL"
   - It should already be set to: `https://lamaq-signlink-hackx.hf.space`
   - If not, paste the URL and it will auto-save

3. **Verify Configuration**:
   - The extension automatically saves the URL to Chrome storage
   - You can change it anytime by clicking the extension icon

---

### Step 3: Test on YouTube

1. **Open a YouTube Video** with captions:
   - Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   - Or any video with closed captions

2. **Enable Captions**:
   - Click the **CC** button on the YouTube video player
   - Ensure captions are visible at the bottom of the video

3. **Start Caption Capture**:
   - Click the **Intellify extension icon** (🤟)
   - Click the **"Start Caption Capture"** button
   - The button should change to "Stop Caption Capture"

4. **Watch the Magic Happen** ✨:
   - A **black overlay window** appears in the bottom-right corner
   - As captions appear on YouTube, ASL videos play in the overlay
   - Each word gets translated to sign language video

---

## 🔍 What to Expect

### Normal Behavior:

✅ **Overlay Appears**: Black video player in bottom-right (320x180px)  
✅ **Caption Detection**: Console logs show `[Intellify] Caption detected: "..."`  
✅ **Token Processing**: Videos load for each word  
✅ **Queue System**: Multiple captions queue up and play sequentially  
✅ **No Duplicates**: Same caption within 3 seconds won't trigger re-processing  

### Visual Indicators:

- **"Loading..."**: Fetching video from backend
- **Video Playback**: ASL sign playing
- **Empty State**: "Waiting for captions..." when idle
- **Error State**: Red text if backend connection fails

---

## 🛠️ Testing Checklist

### ✅ Basic Functionality
- [ ] Extension loads without errors
- [ ] Backend URL configured to production
- [ ] YouTube page loads normally
- [ ] Extension icon is clickable
- [ ] Popup shows correct UI

### ✅ Caption Detection
- [ ] Click "Start Caption Capture"
- [ ] YouTube captions are visible
- [ ] Console shows `[Intellify] Caption detected: "..."`
- [ ] Overlay container appears on page

### ✅ Video Translation
- [ ] Videos appear in the overlay window
- [ ] Videos play automatically
- [ ] Multiple words queue and play in sequence
- [ ] Videos are clear and correctly sized

### ✅ Backend Integration
- [ ] `/tokenize-text` API returns tokens
- [ ] `/token-video/{token}` returns video URLs
- [ ] CORS headers allow extension requests
- [ ] Videos load from WLASL cache or download

### ✅ Error Handling
- [ ] Missing words show warning in console
- [ ] Network errors display error message
- [ ] Queue can be cleared via "Clear Queue" button
- [ ] Stop/Start toggle works correctly

---

## 🐛 Debugging

### Open Browser Console:
1. Right-click on YouTube page → **Inspect**
2. Go to **Console** tab
3. Filter by `[Intellify]` to see extension logs

### Expected Console Logs:
```javascript
✅ Intellify content script loaded
[Intellify] Backend URL loaded: https://lamaq-signlink-hackx.hf.space
[Intellify] Caption capture started
[Intellify] Caption detected: "Hello world"
[Intellify] Processing caption: "Hello world"
[Intellify] Tokenizing: "Hello world"
Backend URL: https://lamaq-signlink-hackx.hf.space
[Intellify] Tokenized into 2 tokens: ["hello", "world"]
[Intellify] Fetching video for token: hello
[Intellify] Video enqueued for token: hello
```

### Common Issues & Fixes:

#### ❌ "Failed to fetch" Error
**Cause**: CORS policy blocking requests  
**Fix**: Add CORS headers to backend (already configured):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows extension
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### ❌ "No video found for token"
**Cause**: Word not in WLASL database (2000 glosses)  
**Expected**: Not all English words have ASL videos  
**Fix**: Extension skips missing words automatically

#### ❌ Overlay doesn't appear
**Cause**: Content script didn't inject  
**Fix**: Reload YouTube page, ensure you're on `youtube.com/watch?v=...`

#### ❌ Captions not detected
**Cause**: YouTube caption format changed or captions disabled  
**Fix**: 
1. Ensure CC button is active
2. Check console for caption detection logs
3. Try different video with auto-generated captions

---

## 📊 Backend Endpoints Used

### 1. POST `/tokenize-text`
**Purpose**: Convert caption text into ASL gloss tokens

**Request**:
```json
{
  "text": "Hello world"
}
```

**Response**:
```json
{
  "tokens": ["hello", "world"],
  "original_text": "Hello world"
}
```

### 2. GET `/token-video/{token}`
**Purpose**: Get video URL for a specific sign

**Request**:
```
GET /token-video/hello
```

**Response**:
```json
{
  "token": "hello",
  "video_url": "/tmp/asl_video_cache/hello_69213.mp4",
  "source": "aslbrick"
}
```

---

## 🎯 Test Scenarios

### Scenario 1: Simple Caption
1. Video: Any with simple English captions
2. Expected: Each word gets translated
3. Result: Videos play sequentially in overlay

### Scenario 2: Fast Captions (Rap/Fast Speech)
1. Video: Fast-talking content
2. Expected: Captions queue up and play in order
3. Result: Queue system handles backlog smoothly

### Scenario 3: Missing Words
1. Video: Technical jargon or uncommon words
2. Expected: Console warnings for missing tokens
3. Result: Extension skips missing words, plays available ones

### Scenario 4: Stop/Start Toggle
1. Start caption capture
2. Stop after a few captions
3. Start again
4. Expected: Clean start/stop with no memory leaks

### Scenario 5: Multiple Tabs
1. Open extension in 2 YouTube tabs
2. Start capture in both
3. Expected: Each tab runs independently

---

## 📁 Extension Files

```
chrome_extension/
├── manifest.json          # Extension configuration
├── content.js            # Main logic (caption detection, video queue)
├── popup.html            # Settings UI
├── popup.js              # Settings logic
├── background.js         # Service worker
└── README.md             # Documentation
```

---

## 🔧 Advanced Configuration

### Change Backend URL Mid-Session:
1. Click extension icon
2. Edit "Backend URL" field
3. New URL saves automatically
4. Reload YouTube page for changes to take effect

### Toggle Capture State:
- **Start**: Begins caption monitoring
- **Stop**: Pauses translation (queue still plays)
- **Clear Queue**: Removes all pending videos

### Debug Mode:
Open console and run:
```javascript
// See current queue
console.log(videoQueue);

// Check backend URL
console.log(backendUrl);

// Force process caption
processCaption("test caption");
```

---

## ✅ Success Criteria

Your extension is working correctly if:

1. ✅ **Loads without errors** in `chrome://extensions/`
2. ✅ **Connects to production backend** (https://lamaq-signlink-hackx.hf.space)
3. ✅ **Detects YouTube captions** (console logs show detection)
4. ✅ **Displays overlay** with ASL videos
5. ✅ **Plays videos sequentially** without freezing
6. ✅ **Handles missing words gracefully** (skips with warning)
7. ✅ **Can stop/start cleanly** via toggle button

---

## 🎬 Demo Workflow

**Full Test (2 minutes):**

1. Load extension in Chrome ✅
2. Set backend URL to production ✅
3. Open YouTube video with captions ✅
4. Enable CC button ✅
5. Click extension → Start Caption Capture ✅
6. Watch overlay appear with ASL videos ✅
7. Verify console logs show tokenization ✅
8. Test Clear Queue button ✅
9. Test Stop/Start toggle ✅
10. Success! 🎉

---

## 📝 Notes

- **WLASL Dataset**: 2000 signs available, not all English words covered
- **Queue System**: Prevents duplicate captions within 3-second window
- **Video Source**: Downloads from `aslbrick` and other WLASL sources
- **Cache**: Backend caches videos in `/tmp` (ephemeral on HF Spaces)
- **Performance**: ~1-2 second delay from caption to video playback

---

## 🆘 Need Help?

### Check Console Logs:
```javascript
// Filter by extension messages
[Intellify]
```

### Verify Backend:
```bash
curl https://lamaq-signlink-hackx.hf.space/health
# Should return: {"status": "healthy"}
```

### Test Tokenization Manually:
```bash
curl -X POST https://lamaq-signlink-hackx.hf.space/tokenize-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

### Test Video Endpoint:
```bash
curl https://lamaq-signlink-hackx.hf.space/token-video/hello
```

---

**Happy Testing! 🚀🤟**
