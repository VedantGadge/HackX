# ✅ SETUP CHECKLIST - Extension with Debug Mode

## Prerequisites Checklist

- [ ] **Python 3.8+** installed
  - Check: Open PowerShell, type `python --version`
  
- [ ] **Chrome/Edge browser** (version 100+)
  - Check: Type `chrome://version` in address bar
  
- [ ] **Backend files** present
  - Location: `D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\app.py`
  - Check: File exists and opens
  
- [ ] **Videos folder** exists
  - Location: `D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\videos\`
  - Check: Folder exists (can be empty initially for testing)

- [ ] **Extension files** present
  - Location: `D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\chrome_extension\`
  - Check: Folder contains manifest.json, content.js, popup.html, etc.

---

## Setup Steps Checklist

### Phase 1: Start Backend

- [ ] Open PowerShell or Terminal
  
- [ ] Navigate to project folder
  ```powershell
  cd D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
  ```
  
- [ ] Start the backend server
  ```powershell
  python app.py
  ```
  
- [ ] Verify it's running
  - Check: Terminal shows `Running on http://127.0.0.1:5000`
  - Alternative test:
    ```powershell
    curl http://127.0.0.1:5000/health
    ```
  - Should return: `{"status":"ok"}`

✅ **Backend Status**: Running

---

### Phase 2: Load Extension

- [ ] Open Chrome/Edge browser
  
- [ ] Go to extension page
  - Type in address bar: `chrome://extensions`
  
- [ ] Enable Developer Mode
  - Look for toggle in top-right corner
  - Click to turn ON (should be blue)
  
- [ ] Click "Load unpacked"
  - Button should appear next to other buttons
  
- [ ] Select extension folder
  - Navigate to: `D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\chrome_extension`
  - Click "Select Folder"
  
- [ ] Verify extension loaded
  - Should see "Intellify" in the extension list
  - Should show as "enabled" with a colored icon
  - No red error messages

✅ **Extension Status**: Loaded

---

### Phase 3: Test on YouTube

- [ ] Go to YouTube.com
  ```
  https://www.youtube.com
  ```
  
- [ ] Find a video with captions
  - Look for videos with CC icon
  - Or manually enable auto-generated captions
  
- [ ] Open DevTools Console
  - Press: **F12**
  - Click: **Console** tab
  - You should see: `✅ Intellify content script loaded`
  
- [ ] Enable captions on video
  - Look for **CC** button in video player
  - Click to enable captions
  - Captions should appear at bottom of video
  
- [ ] Start Caption Capture
  - Click Intellify icon (top-right of browser)
  - Click: **"Start Caption Capture"** button
  - Check console, should see:
    ```
    🎬 Starting caption capture...
    📊 Found 1 caption container(s)
    ✅ Caption capture started
    ```

- [ ] Play the video
  - Let video play with captions
  - Watch console for:
    ```
    📝 New caption detected: "..."
    ```

- [ ] Verify backend communication
  - When caption appears, console should show:
    ```
    🌐 TOKENIZATION REQUEST
    Backend URL: http://127.0.0.1:5000
    ⏱️ Response time: XXms
    ✅ TOKENIZATION SUCCESS
    ```

- [ ] Check for available videos
  - Console should show:
    ```
    Available in videos_: 45 tokens
    ```
    (Or however many .mp4 files you have)

- [ ] Watch for video playback
  - Console should show:
    ```
    ▶️ PLAYING VIDEO CLIP
    Token: [word]
    ```

✅ **YouTube Testing**: Complete

---

## Debug Verification Checklist

### Console Logs Should Show

- [ ] `✅ Intellify content script loaded` on page load
  
- [ ] `🎬 Starting caption capture...` when you click Start
  
- [ ] `📊 Found 1 caption container(s)` with at least 1
  
- [ ] `📝 New caption detected:` when captions change
  
- [ ] `🌐 TOKENIZATION REQUEST` when sending to backend
  
- [ ] `✅ TOKENIZATION SUCCESS` when backend responds
  
- [ ] `   Mapped tokens: [...]` showing at least some tokens
  
- [ ] `▶️ PLAYING VIDEO CLIP` showing video is playing
  
- [ ] `✅ Finished playing:` when each video completes

### If Something's Missing

| Missing Log | Problem | Fix |
|---|---|---|
| No console logs at all | Extension not loaded | Reload extension |
| `Found 0 container` | Captions not detected | Enable CC button |
| `NETWORK ERROR` | Backend not running | Start `python app.py` |
| `Mapped tokens: []` | No videos available | Add .mp4 to videos/ |
| No playback logs | Video element issue | Check DevTools errors |

---

## Troubleshooting Checklist

### If Extension Won't Load

- [ ] Check manifest.json exists and is valid
  - File: `chrome_extension/manifest.json`
  - Should start with: `{"manifest_version": 3,`
  
- [ ] Verify no icon errors
  - Should NOT have `"icons"` section (or it should be valid)
  
- [ ] Reload extension
  - Go to `chrome://extensions`
  - Click refresh button (🔄) on Intellify
  
- [ ] Hard refresh YouTube
  - Press: **Ctrl+Shift+R**

### If Captions Not Detected

- [ ] Enable CC on YouTube
  - Look for CC button in video player
  - Click to turn captions ON
  
- [ ] Verify console shows caption attempts
  - Should show: `🔍 Trying alternative selectors...`
  
- [ ] Try different YouTube video
  - Some videos may not have properly formatted captions
  
- [ ] Check YouTube page structure
  - Right-click on caption → Inspect
  - Look for class names containing "caption"
  
- [ ] If issue persists
  - Share the console output
  - Include: Which YouTube video, exact error messages

### If Backend Not Responding

- [ ] Verify backend is running
  - Check terminal shows: `Running on http://127.0.0.1:5000`
  
- [ ] Test backend directly
  ```powershell
  curl http://127.0.0.1:5000/health
  ```
  Should return: `{"status":"ok"}`
  
- [ ] Check backend URL in extension
  - Click Intellify icon
  - Verify URL is: `http://127.0.0.1:5000`
  
- [ ] Check for Python errors
  - Look in terminal for error messages
  - Should say `* Running on...` not error traces
  
- [ ] Restart backend
  ```powershell
  # Stop with Ctrl+C
  # Then:
  python app.py
  ```

### If Videos Not Playing

- [ ] Verify videos folder has files
  ```powershell
  Get-ChildItem D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\videos -Filter "*.mp4"
  ```
  Should list .mp4 files
  
- [ ] Check console shows mapped tokens
  - Should show: `Mapped tokens: [we, go, college]` (or similar)
  - NOT: `Mapped tokens: []`
  
- [ ] If empty, add some test videos
  - Create simple .mp4 files
  - Name them: `hello.mp4`, `world.mp4`, etc.
  
- [ ] Restart backend after adding videos
  - Backend scans videos/ on startup
  
- [ ] Check Network tab for video requests
  - F12 → Network
  - Look for `/token-video/` requests
  - Should show 200 or 206 status

---

## Performance Checklist

- [ ] Backend starts within 3 seconds
- [ ] Extension loads without errors
- [ ] Console logs appear within 100ms of caption changes
- [ ] Backend responds within 500ms
- [ ] Videos start playing within 500ms of being queued
- [ ] Overall latency < 1 second from caption to video playback

---

## Final Verification Checklist

Before considering setup complete:

- [ ] Extension loads without errors
- [ ] Console shows content script loaded
- [ ] YouTube captions are detected
- [ ] Backend responds to requests
- [ ] At least one video plays in overlay
- [ ] No JavaScript errors in console
- [ ] Network requests show 200 status codes
- [ ] All debug logs are visible and readable

---

## Success Criteria

✅ You're done when you see:

1. Extension icon in Chrome toolbar
2. Overlay appears on YouTube video (bottom-right)
3. Console shows debug logs when captions appear
4. Backend responds with token list
5. Videos play sequentially in the overlay
6. All logs show successful operation (✅ not ❌)

---

## Documentation to Read

After setup, review these for details:

1. **Quick Reference**: `QUICK_DEBUG_REFERENCE.md`
   - One page overview
   - Common errors
   - Quick fixes

2. **Debug Guide**: `chrome_extension/DEBUG_GUIDE.md`
   - Detailed troubleshooting
   - Log interpretation
   - Advanced debugging

3. **Full Setup**: `EXTENSION_SETUP.md`
   - Complete guide
   - All options
   - Advanced configuration

---

## Command Reference

### Start Backend
```powershell
cd D:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
python app.py
```

### Check Backend Health
```powershell
curl http://127.0.0.1:5000/health
```

### List Videos
```powershell
Get-ChildItem videos -Filter "*.mp4"
```

### Reload Extension
```
chrome://extensions → Find Intellify → Click 🔄
```

### Hard Refresh YouTube
```
Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

### Clear Cache (if needed)
```
F12 → Application → Cache Storage → Clear All
```

---

## Getting Help

If something doesn't work:

1. **Check console logs** (F12 → Console)
2. **Read the debug log** (tells you what's happening)
3. **Follow troubleshooting section** above
4. **If still stuck, gather**:
   - Console log output (copy/paste)
   - Screenshots showing the issue
   - Steps you took to reproduce
   - Backend terminal output

---

## Version Info

- **Extension Version**: 1.0.0
- **Status**: ✅ Ready with Enhanced Debugging
- **Last Updated**: October 30, 2025
- **Chrome Support**: Version 100+
- **Python Support**: 3.8+

---

**You're all set!** 🚀

Go through this checklist and let me know if you hit any issues. The debug logs will help identify exactly where the problem is.

Good luck! 🤟
