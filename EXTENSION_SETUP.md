# 🤟 Intellify Chrome Extension - Complete Setup Guide

## What is Intellify?

Intellify is a **real-time YouTube caption → sign language translator** that works as a Chrome extension. When you watch a YouTube video with captions enabled, Intellify:

1. **Captures** captions in real-time
2. **Tokenizes** them into sign language components
3. **Queues** the corresponding video clips
4. **Plays** them sequentially in a floating overlay window (Picture-in-Picture)

**Result**: You get simultaneous signed translation of YouTube videos! 🎥➡️🤟

---

## 🚀 Quick Start (5 minutes)

### Step 1: Start the Backend
```bash
# Open a terminal/PowerShell
cd d:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
python app.py
```
You should see:
```
 * Running on http://127.0.0.1:5000
 * DEBUG=True
```

### Step 2: Load the Extension
1. Open Chrome → `chrome://extensions`
2. Toggle **Developer mode** (top-right) ON
3. Click **Load unpacked**
4. Select `d:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\chrome_extension`
5. ✅ Extension loaded!

### Step 3: Test It
1. Go to **youtube.com**
2. Find any video with English captions
3. **Enable captions** (CC button in player)
4. Click **Intellify extension** icon → "Start Caption Capture"
5. **Play the video** 🎬
6. Watch reverse translation clips appear in the floating overlay! 🤟

---

## 📋 System Requirements

| Component | Requirement | Check |
|-----------|-------------|-------|
| **Chrome** | Version 100+ | Type `chrome://version` in URL bar |
| **Python** | 3.8+ | `python --version` |
| **Backend** | app.py running | Should show "Running on http://127.0.0.1:5000" |
| **Video Library** | `videos/*.mp4` files | Check `videos/` folder for token files |
| **Disk Space** | ~100MB+ | For video files |

---

## 📁 File Structure

```
d:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\
├── app.py                          ← Backend Flask server
├── videos/                         ← Sign language token videos
│   ├── we.mp4
│   ├── go.mp4
│   ├── college.mp4
│   └── ... (add more token videos here)
├── chrome_extension/               ← Extension folder (load this!)
│   ├── manifest.json              # Extension metadata
│   ├── content.js                 # Main extension logic
│   ├── popup.html                 # Extension popup UI
│   ├── popup.js                   # Popup event handlers
│   ├── background.js              # Service worker
│   ├── README.md                  # Detailed extension docs
│   ├── TESTING.md                 # Testing checklist
│   ├── API_CONTRACT.md            # Backend API reference
│   └── (images/ folder would go here for icons)
├── templates/
│   └── index.html                 ← Main app (uses YouTube IFrame API)
└── static/
    └── script.js                  ← Frontend logic
```

---

## 🔧 Configuration

### Backend URL
The extension connects to the backend at `http://127.0.0.1:5000` by default.

**To change it**:
1. Click Intellify extension icon
2. Enter new URL in the "Backend URL" field
3. Save automatically via browser storage

**Examples**:
- Local: `http://127.0.0.1:5000`
- Remote: `http://192.168.1.100:5000`
- Production: `https://intellify.example.com`

### Video Library
Add more sign language tokens:
1. Place `.mp4` files in the `videos/` folder
2. Name them by token: `hello.mp4`, `world.mp4`, `how.mp4`, etc.
3. Backend automatically discovers new files (restart not needed)

---

## 🎯 How It Works

### User Flow
```
User watches YouTube 
         ↓
Caption appears on screen
         ↓
Extension detects caption (MutationObserver)
         ↓
Sends to backend: "We are going to college"
         ↓
Backend tokenizes: ["we", "are", "go", "to", "college"]
         ↓
Extension filters available: ["we", "go", "college"] ✓
         ↓
Queue plays clips: we.mp4 → go.mp4 → college.mp4
         ↓
User sees videos in bottom-right overlay! 🎥
```

### Token Mapping Logic
Backend is smart about matching tokens to videos:

| Scenario | Example | Mapping |
|----------|---------|---------|
| **Exact Match** | "hello" | ✓ hello.mp4 exists |
| **Stemming** | "going" | → "go" (removes -ing suffix) |
| **Synonyms** | "exam" | → "test" (synonym map) |
| **Fuzzy Match** | "helo" (typo) | → "hello" (89% similarity) |
| **No Match** | "xyzabc" | ✗ Skipped, shown in "missing" |

---

## 🧪 Testing Checklist

### Prerequisites
- [ ] Backend running at http://127.0.0.1:5000
- [ ] Extension loaded in chrome://extensions
- [ ] YouTube page open
- [ ] Test video with captions available

### Test Steps
1. [ ] Click extension icon → Verify Backend URL is correct
2. [ ] Enable captions on YouTube (CC button)
3. [ ] Click "Start Caption Capture" button
4. [ ] Play video with English captions
5. [ ] Watch overlay play sign language videos
6. [ ] Check caption bar shows "Next: [tokens]"
7. [ ] Click "Clear Queue" → videos stop
8. [ ] Click "Start Caption Capture" again → toggle off
9. [ ] Reload page → extension still works

### Success Indicators ✅
- [ ] Overlay visible at bottom-right of player (320×180px)
- [ ] Toggle button is clickable
- [ ] Console shows "[Intellify] content script loaded"
- [ ] When caption appears: "📝 New caption: ..."
- [ ] Videos play in overlay
- [ ] No errors in Chrome DevTools (F12 → Console)

---

## 🐛 Troubleshooting

### Issue: "Overlay not visible"
**Solution**:
- Reload extension: chrome://extensions → Intellify → Reload
- Hard refresh YouTube page: Ctrl+Shift+R
- Check z-index in DevTools: Inspector → #intellify-reverse-overlay should have z-index: 9999

### Issue: "Captions not detected"
**Solution**:
- Enable captions first (CC button on player)
- Check DevTools Console (F12 → Console) for errors
- Look for: `⚠️ No caption containers found` message
- Try different videos or YouTube pages
- YouTube DOM structure may have changed; check selector in content.js

### Issue: "No videos playing"
**Solution**:
- Backend may not be running: `python app.py` in terminal
- Check Network tab (F12 → Network):
  - POST /tokenize-text should return 200 ✓
  - GET /token-video/[token] should return 200 or 206 ✓
- Verify videos/ folder has .mp4 files
- Check token names match filename (lowercase, no spaces)

### Issue: "Connection failed to backend"
**Solution**:
- Verify backend URL in extension popup (default: http://127.0.0.1:5000)
- Ensure Python server is running
- Check CORS headers: Backend should respond with `Access-Control-Allow-Origin: *`
- Try ping from PowerShell: `curl http://127.0.0.1:5000/health`

### Issue: "Wrong token is playing"
**Solution**:
- This is the token mapping algorithm working correctly
- Check console for "missing: [...]" to see unmapped tokens
- Add more videos to videos/ folder or expand synonym map in app.py

### Issue: "Browser crashes or extension is slow"
**Solution**:
- Check if too many videos are queued (should auto-clear after playing)
- Try clearing cache: chrome://settings → Privacy → Clear browsing data
- Reduce video size/quality in videos/ folder
- Restart browser

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Detailed installation & troubleshooting (in chrome_extension/) |
| **TESTING.md** | Quick checklist for testing the extension |
| **API_CONTRACT.md** | Backend API reference & data flow diagrams |

---

## 🔍 Debugging Tips

### View Extension Logs
1. Go to any YouTube page with extension loaded
2. Open DevTools: **F12**
3. Go to **Console** tab
4. You should see logs like:
   ```
   ✅ Intellify content script loaded
   🎬 Starting caption capture...
   📝 New caption: We are going to college
   🌐 Tokenizing caption: We are going to college
   ▶️ Playing token: we
   🧹 Queue cleared
   ```

### Check Network Requests
1. **F12** → **Network** tab
2. Filter by "Fetch/XHR"
3. Play a video with captions
4. You should see:
   - `POST /tokenize-text` with response containing token array
   - `GET /token-video/[token]` requests returning video data

### Inspect Overlay Element
1. **F12** → **Inspector** tab
2. Click the picker tool (top-left)
3. Click on the overlay window (bottom-right)
4. You should see: `<div id="intellify-reverse-overlay">`

---

## 🚨 Common Errors & Solutions

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `TypeError: Failed to fetch` | Backend not running | Start Python app.py |
| `Uncaught SyntaxError in popup.js` | JS syntax error | Check file for brackets, semicolons |
| `No caption containers found` | YouTube DOM changed | Update selector in content.js |
| `404 /token-video/hello` | Video file missing | Add hello.mp4 to videos/ folder |
| `CORS error` | Backend missing CORS headers | Ensure Flask app has CORS enabled |
| `Extension not loaded` | Invalid manifest.json | Verify manifest syntax |

---

## 📊 Performance Metrics

| Metric | Expected Value |
|--------|-----------------|
| Extension load time | <100ms |
| Caption detection latency | 50-200ms (YouTube dependent) |
| Tokenization latency | 100-500ms (LLM or heuristic) |
| Video playback startup | 50-150ms |
| Memory usage | 30-80MB |

---

## 🔐 Security & Privacy

✅ **What's Secure**:
- Extension only runs on youtube.com
- Captions are not logged or stored long-term
- Communication with backend is local (or use HTTPS for remote)
- No third-party trackers

⚠️ **What's Not**:
- Backend URL and video tokens are stored in browser storage
- HTTPS not enforced (use it for production!)
- Extension has broad access to YouTube pages (trusted software)

---

## 🎓 Learning Resources

- **YouTube IFrame API**: https://developers.google.com/youtube/iframe_api_reference
- **Chrome Extension Manifest v3**: https://developer.chrome.com/docs/extensions/mv3/
- **MutationObserver API**: https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver
- **Flask Web Framework**: https://flask.palletsprojects.com/

---

## 📞 Support & Next Steps

### Getting Help
1. Check the **TESTING.md** checklist
2. Review **README.md** in chrome_extension/
3. Check browser console logs (F12)
4. Verify backend is running: `python app.py`
5. Test backend directly: `curl http://127.0.0.1:5000/health`

### Future Enhancements
- [ ] Draggable overlay
- [ ] Adjustable overlay size
- [ ] Multiple caption track support
- [ ] Offline mode
- [ ] Custom video library uploader
- [ ] WebRTC peer translation
- [ ] Mobile app (React Native)

### Contributing
To improve Intellify:
1. Add more .mp4 files to videos/ folder
2. Expand synonym map in app.py
3. Improve LLM tokenization (modify revtrans.py)
4. File issues/PRs on GitHub (when available)

---

## 📝 Version Info

- **Extension Version**: 1.0.0
- **Chrome Requirement**: 100+
- **Python Requirement**: 3.8+
- **Backend Framework**: Flask 2.0+
- **Last Updated**: 2024

---

## 🎉 You're Ready!

Now go load the extension and test it on YouTube! 

**Next steps**:
1. Make sure backend is running: `python app.py`
2. Go to `chrome://extensions`
3. Load unpacked → select chrome_extension/ folder
4. Visit youtube.com and start translating! 🤟

---

**Questions?** Check the documentation files in chrome_extension/ or review the API_CONTRACT.md for backend details.

**Happy translating!** 🎬→🤟
