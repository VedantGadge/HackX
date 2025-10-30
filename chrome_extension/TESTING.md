# Intellify Extension - Quick Start Checklist

## Before Testing
- [ ] Backend server running: `python app.py`
- [ ] Backend responding at http://127.0.0.1:5000 (test with browser)
- [ ] `videos/` directory has .mp4 files (at least: we.mp4, go.mp4, college.mp4)

## Installation Checklist
- [ ] Navigate to `chrome://extensions`
- [ ] Toggle **Developer mode** ON (top-right)
- [ ] Click **Load unpacked**
- [ ] Select the `chrome_extension/` folder
- [ ] Verify extension appears in list with icon

## First Test Run
1. [ ] Go to youtube.com
2. [ ] Find a video with English captions (or use a caption test file)
3. [ ] Click extension icon → Verify Backend URL is `http://127.0.0.1:5000`
4. [ ] Enable captions on video (CC button)
5. [ ] Click **"Start Caption Capture"** in overlay
6. [ ] Play video or speak captions manually
7. [ ] Watch overlay video play along with captions
8. [ ] See "Next: token · token · token" in caption bar


## Test Transcript Examples
Try these sentences (should tokenize to available tokens):

**Example 1**: "We are going to college"
- Expected tokens: [we, are, go, college]
- Mapped tokens: [we, go, college] (assuming those videos exist)

**Example 2**: "Hello world"
- Expected tokens: [hello, world]
- Mapped tokens: [hello, world] (if hello.mp4 and world.mp4 exist)

## Debugging Checklist
- [ ] Open DevTools (F12)
- [ ] Go to Console tab
- [ ] Check for errors starting with `[Intellify]`
- [ ] Verify logs show "New caption: ..." when speaking
- [ ] Check Network tab for POST `/tokenize-text` requests
- [ ] Verify responses include `tokens` array
- [ ] Check for GET `/token-video/<token>` requests (200 or 206 status)

## Quick Fixes
| Issue | Fix |
|-------|-----|
| Overlay not visible | Reload extension (chrome://extensions → Reload) or hard refresh page |
| Captions not detected | Enable CC on video, check selector in content.js |
| Backend connection fails | Verify server running, URL in popup matches |
| No videos play | Check videos/ has files, backend /token-video returns 200 |
| Random token doesn't work | Add synonym to SYN map in app.py or create video file |

## Files to Check
| File | Purpose | Quick Check |
|------|---------|------------|
| `manifest.json` | Extension metadata | Contains youtube.com permissions |
| `content.js` | Main logic | Check console.log statements |
| `popup.js` | Popup handlers | Verify button IDs match popup.html |
| `popup.html` | Popup UI | Check for toggleBtn, clearBtn IDs |
| `background.js` | Service worker | Minimal, no errors expected |
| `app.py` | Backend | GET http://127.0.0.1:5000/health should return 200 |
| `videos/` | Token files | List with `dir videos\ /b` or `ls videos/` |

## Reset/Reload Steps
1. Go to chrome://extensions
2. Find "Intellify" extension
3. Click the 🔄 (reload) button
4. Go back to YouTube page
5. Hard refresh (Ctrl+Shift+R on Windows)
6. Try again

## Success Indicators ✅
- Extension icon appears in Chrome toolbar
- Overlay appears at bottom-right of YouTube player
- Console shows "[Intellify] content script loaded"
- Clicking buttons shows "toggled" messages
- Captions trigger "New caption: ..." messages
- Videos play in overlay as captions appear
- Network requests show 200-status responses

---

**Need Help?** Check the full README.md in chrome_extension/ folder
