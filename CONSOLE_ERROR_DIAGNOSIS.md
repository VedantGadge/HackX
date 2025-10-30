# 🆘 Console Error Diagnosis & Solution

## What You're Seeing

```
Intellify content script loaded
[Violation] Permissions policy violation: unload is not allowed
Failed to load resource: status 403
✅ Overlay initialized
✅ Intellify ready on youtube.com
🎬 Starting caption capture...
⚠️ No caption containers found
🎯 Caption capture started from popup
```

---

## Error Analysis

### 1. **Permissions Policy Violation** ❌ **NOT OUR PROBLEM**

```
[Violation] Permissions policy violation: unload is not allowed
```

**What it is:** YouTube's security setting (Permissions Policy)  
**Cause:** YouTube blocks certain browser actions for security  
**Impact on Intellify:** NONE - Our extension doesn't use unload events  
**Status:** ✅ Can safely ignore

---

### 2. **Failed to Load Resource: 403** ❌ **NOT OUR PROBLEM**

```
Failed to load resource: the server responded with a status of 403
```

**What it is:** YouTube video loading issue  
**Cause:** 
- Network timeout
- Geographic restriction
- YouTube rate limiting
- Video encoding variant not available

**Impact on Intellify:** NONE - Our extension doesn't load videos from YouTube directly  
**Status:** ✅ Can safely ignore

---

### 3. **No Caption Containers Found** ✅ **THIS IS THE REAL ISSUE**

```
🎬 Starting caption capture...
⚠️ No caption containers found. Make sure captions are enabled on the video.
```

**What it means:** Captions are NOT currently visible on YouTube  
**Why it happens:** 
- CC (closed captions) button NOT clicked
- Video doesn't have captions available
- Captions are turned off

**Impact on Intellify:** ❌ **CANNOT capture captions if they're not visible**  
**Status:** ⚠️ **ACTION REQUIRED**

---

## ✅ How to Fix

### Step 1: Enable Captions on YouTube

```
1. Find the video player
2. Look for "CC" button in bottom-right corner
3. Click it → Captions should appear with white text
4. Look for a dropdown to select language if needed
```

### Step 2: Check Console Again

After enabling CC, you should see:

```
🎬 Starting caption capture...
🔍 Trying selector ".captions-text": found 0 element(s)
🔍 Trying selector ".ytp-caption-segment": found 2 element(s)
✅ Using selector: .ytp-caption-segment
📌 Observing container 1/2
📌 Observing container 2/2
✅ Caption capture started - watching for caption changes
💡 Backup polling enabled every 1 second
```

### Step 3: Watch for Caption Detection

When a caption appears:

```
📝 New caption detected: "Your caption text here"
🌐 TOKENIZATION REQUEST
Backend URL: http://127.0.0.1:5000
📤 Sending to backend...
⏱️ Response time: 150ms
📊 Response status: 200 OK
✅ TOKENIZATION SUCCESS
   Mapped tokens: [we, go, college]
```

Then overlay videos should start playing!

---

## Troubleshooting

### Problem: Still showing "No caption containers"

**Checklist:**
```
☐ 1. CC button visible on video?
     If NO: Video might not have captions
     If YES: Continue...

☐ 2. CC button clicked (captions showing)?
     If NO: Click it now!
     If YES: Continue...

☐ 3. Can you see white text captions on video?
     If NO: Try different language or video
     If YES: Extension should work now...

☐ 4. Hard refresh page (Ctrl+Shift+R)
     Then click "Start Caption Capture" again
```

### Problem: "Captions not available"

Some videos don't have captions. Try these:
- TED Talks (always have captions)
- News videos (usually have captions)
- Search "how to" videos (typically have captions)
- YouTube tutorial channels

### Problem: Captions in other language

Make sure you select **English** captions:
1. Click CC button
2. Click the gear/settings icon
3. Select English

---

## What Each Message Means

| Console Output | Meaning | Status |
|---|---|---|
| `🎬 Starting caption capture...` | Starting to look for captions | ✅ Good |
| `🔍 Trying selector...` | Testing different CSS selectors | ✅ Good |
| `✅ Using selector: ...` | Found captions! | ✅ Good |
| `⚠️ No caption containers found` | Captions not visible | ⚠️ Action needed |
| `💡 Make sure captions are ENABLED` | Click CC button | ⚠️ Action needed |
| `✅ Fallback polling started` | Monitoring for captions | ✅ Good |
| `📝 New caption detected` | Captured a caption! | ✅ Good |
| `🌐 TOKENIZATION REQUEST` | Sending to backend | ✅ Good |
| `❌ NETWORK ERROR` | Backend not running | ❌ Fix needed |
| `✅ TOKENIZATION SUCCESS` | Backend processed caption | ✅ Good |
| `▶️ PLAYING VIDEO CLIP` | Sign language video playing | ✅ Good |

---

## The Flow (with Captions Enabled)

```
Extension loads
    ↓
"Start Caption Capture" clicked
    ↓
Extension looks for caption containers
    ↓
    IF found:
        ├─ Sets up observer (real-time detection)
        └─ Sets up polling (backup)
    ↓
    IF NOT found:
        ├─ Shows big warning message
        ├─ Sets up polling to look for captions
        ├─ Waits for user to enable CC
        └─ Auto-switches to observer once CC enabled
    ↓
Caption appears on YouTube
    ↓
Extension captures it
    ↓
Sends to backend for tokenization
    ↓
Backend returns tokens (sign language words)
    ↓
Sign language videos queued
    ↓
Videos play in overlay (bottom-right)
```

---

## Quick Checklist Before Testing

```
✓ Backend running: python app.py
✓ Videos folder exists: D:\...\videos\
✓ Videos folder has .mp4 files
✓ YouTube video open
✓ CC button visible on video player
✓ CC button CLICKED (captions showing)
✓ DevTools open (F12)
✓ Console tab open
✓ Extension icon visible in toolbar
✓ Click "Start Caption Capture" button
```

If all ✓ → Extension should work!

---

## What Those Network Errors Mean

### `403 Forbidden` errors

YouTube CDN is rejecting video downloads. **This is normal!** It means:
- The video isn't being played
- OR YouTube is restricting that specific format
- Our extension doesn't need YouTube videos anyway (we have our own `videos/` folder)

### `[Violation] Permissions policy` 

YouTube's security. **We don't use that feature**, so it doesn't affect us.

### `Before install prompt prevented` 

Chrome PWA notification. **Completely unrelated** to our extension.

---

## Success Indicators

After enabling CC and clicking "Start Caption Capture", you should see:

```
✅ Using selector: .ytp-caption-segment
✅ Caption capture started
📝 New caption detected: "hello world"
🌐 TOKENIZATION REQUEST
✅ TOKENIZATION SUCCESS
▶️ PLAYING VIDEO CLIP: hello
🎬 OVERLAY VIDEO: Playing in bottom-right corner
```

If you see ALL of these → **WORKING PERFECTLY** 🎉

---

## Next Steps

1. **Reload extension** (chrome://extensions → Reload Intellify)
2. **Go to YouTube video** with captions
3. **Click CC button** to enable captions
4. **Open DevTools** (F12) → Console
5. **Click "Start Caption Capture"** in extension popup
6. **Check console** for success messages
7. **Play video** and watch overlay

---

## Still Having Issues?

**Share these details:**
1. Full console log (copy all text from Console tab)
2. Screenshot showing CC button location
3. Whether captions are visible as white text
4. What backend shows: `curl http://127.0.0.1:5000/health`

---

**Created:** October 30, 2025  
**Purpose:** Explain harmless vs real errors  
**Status:** Updated with better error messaging
