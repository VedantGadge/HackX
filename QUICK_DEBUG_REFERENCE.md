# 📋 Extension Loading & Debugging Quick Reference

## ✅ Fixed Issues

### Issue: "Could not load manifest"
**Fixed by**: Removing the non-existent icons section from manifest.json

**What to do now**: 
1. Go to `chrome://extensions`
2. Click **Reload** button on Intellify extension
3. Should load without errors ✅

---

## 🚀 Step-by-Step Setup

### 1. **Start Backend**
```powershell
cd D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
python app.py
```
✅ You should see: `Running on http://127.0.0.1:5000`

### 2. **Load Extension**
- Go to `chrome://extensions`
- Toggle **Developer mode** ON
- Click **Load unpacked**
- Select `D:\...\chrome_extension` folder
- ✅ Extension should appear with icon

### 3. **Test on YouTube**
- Go to `youtube.com`
- Find video with captions
- Click **CC** button to enable captions
- Click Intellify icon → "Start Caption Capture"
- Play video
- Watch console logs (F12)

---

## 🔍 Debugging Checklist

When testing, check these logs in Console (F12):

| ✅ Expected Log | ❌ If Missing | Fix |
|---|---|---|
| `🎬 Starting caption capture...` | Click "Start" button | Click "Start Caption Capture" |
| `📊 Found 1 caption container(s)` | Enable captions | Click CC button on video |
| `📝 New caption detected:` | Captions not changing | Play video or refresh |
| `🌐 TOKENIZATION REQUEST` | Backend not running | Start `python app.py` |
| `⏱️ Response time: XXms` | Network error | Check backend running |
| `✅ TOKENIZATION SUCCESS` | HTTP error | Check console for error |
| `Mapped tokens: [...]` | Empty array | Add .mp4 files to videos/ |
| `▶️ PLAYING VIDEO CLIP` | No playback | Check videos/ has files |

---

## 📁 Important Folders

```
D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\
├── app.py                    ← Backend server
├── videos/                   ← Token .mp4 files (MUST have files here!)
├── chrome_extension/         ← Extension folder (LOAD THIS!)
│   ├── manifest.json        ← Extension config (FIXED ✅)
│   ├── content.js           ← Main logic (ENHANCED with debug logs)
│   ├── popup.html           ← UI
│   ├── popup.js             ← Button handlers
│   ├── background.js        ← Service worker
│   ├── DEBUG_GUIDE.md       ← Detailed debugging (NEW!)
│   ├── README.md
│   ├── TESTING.md
│   ├── ARCHITECTURE.md
│   └── API_CONTRACT.md
├── EXTENSION_SETUP.md       ← Setup guide
├── DEBUGGING_ACTIVATED.md   ← This file's parent
└── ...
```

---

## 🎯 Common Debug Messages

### ✅ Good - Captions Working
```
🎬 Starting caption capture...
📊 Found 1 caption container(s)
✅ Caption capture started
📝 New caption detected: "We are going to college"
```

### ✅ Good - Backend Responding
```
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
⏱️ Response time: 120ms
📊 Response status: 200 OK
✅ TOKENIZATION SUCCESS
```

### ❌ Bad - No Captions Detected
```
📊 Found 0 caption container(s)
💡 Make sure captions are ENABLED
```
**Fix**: Click CC button on YouTube

### ❌ Bad - Backend Not Running
```
❌ NETWORK ERROR
Error message: Failed to fetch
Attempted URL: http://127.0.0.1:5000/tokenize-text
```
**Fix**: Start backend with `python app.py`

### ❌ Bad - No Video Files
```
Mapped tokens: []
Missing (no video): [we, are, go, college]
Available in videos/: 0 tokens
```
**Fix**: Add .mp4 files to `videos/` folder

---

## 🔄 How to Reload Extension

After making changes:

1. **Go to** `chrome://extensions`
2. **Find** Intellify extension
3. **Click** the 🔄 button (reload)
4. **Go to** youtube.com
5. **Press** Ctrl+Shift+R (hard refresh)
6. **Try again**

---

## 📊 Console Log Filtering

In Chrome DevTools Console:

1. Click **Filter** icon 🔍
2. Type to filter logs:
   - `TOKENIZATION` - show only tokenization
   - `PLAYING` - show only video playback
   - `ERROR` - show only errors
   - `New caption` - show when captions detected

---

## 🎓 Debug Log Sections

Each major operation is wrapped in visual separators:

```
============================================================
🌐 TOKENIZATION REQUEST
[detailed info about the request]
============================================================
```

This makes it easy to see where each operation starts and ends.

---

## 🆘 If Something Goes Wrong

### Extension won't load
1. Check manifest.json has no icon references ✅ (FIXED)
2. Go to chrome://extensions → Reload
3. Check DevTools for error messages

### No captions detected
1. Enable CC on YouTube ✓
2. Check console: should see "Found 1 caption container"
3. If not, try different YouTube videos

### Backend connection fails
1. Check backend is running: `python app.py` ✓
2. Check URL in extension popup (http://127.0.0.1:5000) ✓
3. Test manually: `curl http://127.0.0.1:5000/health`

### Videos not playing
1. Check videos/ folder has .mp4 files ✓
2. Check console: "Available in videos_: X tokens" should be > 0
3. Restart backend if you added new files

---

## 📝 Files to Review

For more details, see:

| File | Purpose |
|------|---------|
| **DEBUG_GUIDE.md** | Complete debugging walkthrough with examples |
| **EXTENSION_SETUP.md** | Full setup instructions |
| **README.md** | Extension documentation |
| **ARCHITECTURE.md** | How all components work together |
| **API_CONTRACT.md** | Backend API details |

---

## ✨ What's New in This Update

✅ **Enhanced Logging**: Every step now has detailed console output
✅ **Better Visibility**: You can see exactly where issues occur
✅ **Auto-Detection**: Tries alternative selectors if main one fails
✅ **Performance Metrics**: Shows response times in milliseconds
✅ **Complete Debugging Guide**: DEBUG_GUIDE.md file for troubleshooting
✅ **Manifest Fixed**: Removed problematic icon references

---

## 🚀 Next Action

1. **Reload extension** (chrome://extensions → Reload)
2. **Go to YouTube** and enable captions
3. **Open Console** (F12)
4. **Click "Start Caption Capture"**
5. **Play a video**
6. **Watch the debug logs** tell you exactly what's happening!

---

**You now have complete visibility into the extension's operation!** 🔍✨

Good luck! Share the console logs if you hit any issues.
