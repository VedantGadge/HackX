# Intellify Chrome Extension - Installation & Setup Guide

## Overview
This Chrome extension captures YouTube video captions in real-time and displays corresponding sign language video translations in a small overlay window (Picture-in-Picture) at the bottom-right of the YouTube player.

## Prerequisites
1. **Backend Server Running**: Make sure the Flask backend (`app.py`) is running on `http://localhost:5000` or `http://127.0.0.1:5000`
   ```bash
   python app.py
   ```

2. **Video Library**: Ensure the `videos/` directory contains `.mp4` files for individual sign language tokens
   ```
   videos/
   ├── we.mp4
   ├── go.mp4
   ├── college.mp4
   ├── ...
   ```

3. **Chrome Browser**: Use Google Chrome (or Chrome-based browsers like Edge, Brave)

## Installation Steps

### Step 1: Load the Extension
1. Open Chrome and navigate to **chrome://extensions**
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `chrome_extension/` folder
5. The extension should now appear in your extensions list

### Step 2: Configure Backend URL (Optional)
1. Click the **Intellify extension icon** in the toolbar (top-right of Chrome)
2. Enter your backend server URL (default: `http://127.0.0.1:5000`)
3. Click anywhere outside the input to save

### Step 3: Enable on YouTube
1. Navigate to any YouTube video page
2. The Intellify overlay should appear at the **bottom-right corner** of the player
3. You should see controls: **"Start Caption Capture"** and **"Clear Queue"** buttons

## Usage

### To Start Real-Time Translation:
1. **Enable captions** on the YouTube video (CC button in player controls)
2. Click **"Start Caption Capture"** in the Intellify overlay
3. As captions appear on the video, the extension will:
   - Tokenize the caption text
   - Queue the corresponding sign language clips
   - Play them sequentially in the overlay window
4. A caption bar shows the current token + next 3 tokens to be played

### To Stop Translation:
1. Click **"Start Caption Capture"** again to toggle it off, or
2. Click **"Clear Queue"** to clear all pending clips and stop playback

## File Structure
```
chrome_extension/
├── manifest.json          # Extension metadata & permissions
├── content.js            # Main logic (injected into youtube.com)
├── background.js         # Service worker (minimal)
├── popup.html            # Extension popup UI
├── popup.js              # Popup event handlers
└── README.md             # This file
```

## Key Features
- ✅ **Real-Time Caption Detection**: Monitors YouTube captions via DOM MutationObserver
- ✅ **Automatic Tokenization**: Sends captions to backend for LLM-based tokenization
- ✅ **Token-to-Video Mapping**: Smart matching with stemming, synonyms, and fuzzy search
- ✅ **Queue-Based Playback**: FIFO queue ensures clips play sequentially
- ✅ **PiP Overlay**: Floating window at bottom-right (320×180px, 16:9 aspect ratio)
- ✅ **Smart Missing Token Handling**: Shows which words couldn't be translated
- ✅ **Configurable Backend**: Backend URL saved via chrome.storage.sync

## Troubleshooting

### "No caption containers found"
**Problem**: Extension logs warning "No caption containers found"
**Solution**: 
- Make sure captions are **enabled** on the YouTube video (CC button)
- YouTube caption DOM structure varies; extension may need selector adjustment
- Check browser console (F12 → Console tab) for detailed logs

### Captions not detected
**Problem**: Overlay appears but captions aren't being captured
**Solution**:
1. Open DevTools (F12)
2. Go to Console tab
3. Check for error messages starting with `[Intellify]`
4. Verify backend URL is correct in extension popup
5. Ensure backend server is running and responding to requests

### Videos not playing
**Problem**: Captions are tokenized but no video clips play
**Solution**:
- Backend server may not be running; start it with `python app.py`
- Ensure `/token-video/<token>` endpoint returns valid MP4 files
- Check that `videos/` directory contains `.mp4` files for the tokens
- Look for 404 or 503 errors in browser Network tab (F12 → Network)

### "Failed to fetch from backend"
**Problem**: Network errors when trying to reach the backend
**Solution**:
- Verify backend server is running: `python app.py`
- Check Backend URL in extension popup matches your server (default: http://127.0.0.1:5000)
- If backend is on a different machine, update the URL accordingly
- Check CORS headers from backend (should have `Access-Control-Allow-Origin: *`)

### Browser console shows "Uncaught TypeError"
**Problem**: JavaScript errors in extension
**Solution**:
- Open DevTools (F12)
- Go to Console tab
- Take note of the error message and line number
- This usually indicates a backend communication issue or DOM selector mismatch

## Advanced Configuration

### Adjusting Caption Selector
If YouTube's DOM structure changes and captions aren't detected:
1. Open `chrome_extension/content.js`
2. Find the line: `const captionContainers = document.querySelectorAll('.captions-text');`
3. Inspect YouTube caption elements (F12 → Inspector)
4. Update the selector to match the actual class/id (e.g., `.ytp-caption-segment`)

### Extending Token Coverage
If certain words aren't being translated:
1. Check the console for "missing tokens" list
2. Add new video files to `videos/` directory
3. Or update the synonym map in `app.py` (search for `SYN =`)

### Building Custom Video Library
To add support for new sign language tokens:
1. Record/create video files for each token
2. Name them as `<token>.mp4` (e.g., `hello.mp4`, `world.mp4`)
3. Place them in the `videos/` directory
4. Backend will automatically detect them

## Debugging

### View Extension Logs
1. Open Chrome DevTools on any YouTube page (F12)
2. Go to **Console** tab
3. You should see logs like:
   ```
   ✅ Intellify content script loaded
   📝 New caption: We are going to college
   🌐 Tokenizing caption: We are going to college
   ▶️ Playing token: we
   ```

### Check Network Requests
1. Open DevTools (F12)
2. Go to **Network** tab
3. Play a YouTube video with captions enabled
4. You should see requests like:
   - `POST /tokenize-text` (returns token list)
   - `GET /token-video/we` (returns video clip)

### View Extension Details
1. Go to chrome://extensions
2. Click **Details** on the Intellify extension
3. View permissions, source code, and reload/uninstall options

## Performance Tips
- Extension uses minimal CPU when captions aren't being captured
- Video clips are cached by backend, so repeated tokens play faster
- Queue processes one clip at a time to avoid overlapping audio
- Overlay is hardware-accelerated (fixed position, z-index)

## Security & Privacy
- Extension only activates on youtube.com
- No user data is collected or transmitted outside the backend
- All processing happens locally (on your machine)
- Backend URL is stored locally in browser storage
- Communication with backend is unencrypted (use HTTPS for production)

## Support & Issues
If you encounter issues:
1. Check this README's Troubleshooting section
2. Review browser console logs (F12 → Console)
3. Verify backend is running and responsive
4. Ensure all files are in the correct locations
5. Try reloading the extension (chrome://extensions → Reload button)

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Tested on**: Chrome 120+
