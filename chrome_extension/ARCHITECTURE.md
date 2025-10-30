# Intellify Extension - Component Architecture

## 📦 Components Overview

```
┌─────────────────────────────────────────────────────────┐
│                    YouTube Website                      │
│  (youtube.com with captions enabled)                    │
└────────┬────────────────────────────────────────────────┘
         │
         │ (Extension injected here)
         ↓
┌─────────────────────────────────────────────────────────┐
│          Chrome Extension (chrome_extension/)            │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ content.js (Main Logic)                         │   │
│  │ - MutationObserver (detect captions)            │   │
│  │ - Queue management (FIFO)                       │   │
│  │ - Video playback control                        │   │
│  │ - Overlay injection & styling                   │   │
│  │ - Message listener (from popup)                 │   │
│  └──────┬────────────────────────────┬─────────────┘   │
│         │                            │                  │
│         │ (fetch API)               │                  │
│         ↓                            │                  │
│  ┌──────────────────┐              │                  │
│  │  popup.html      │              │ (chrome.runtime  │
│  │  popup.js        │              │  .onMessage)     │
│  │  (UI & storage)  │              │                  │
│  └──────────────────┘              │                  │
│                                     │                  │
│  ┌──────────────────┐              │                  │
│  │ background.js    │◄─────────────┘                  │
│  │ (service worker) │                                 │
│  └──────────────────┘                                 │
│                                                        │
│  ┌──────────────────┐                                 │
│  │ manifest.json    │                                 │
│  │ (metadata,       │                                 │
│  │  permissions)    │                                 │
│  └──────────────────┘                                 │
└────────┬─────────────────────────────────────────────┘
         │
         │ (HTTP REST calls)
         ↓
┌─────────────────────────────────────────────────────────┐
│        Flask Backend (app.py)                          │
│        Running on http://127.0.0.1:5000                │
│                                                          │
│  POST /tokenize-text                                   │
│  │  Input: { text: "We are going to college" }        │
│  │  Output: { tokens, tokens_all, missing, available }│
│  └─ LLM (via revtrans) or heuristic tokenization     │
│                                                         │
│  GET /token-video/<token>                              │
│  │  Input: token name (e.g., "we")                    │
│  │  Output: Binary MP4 data                           │
│  └─ Serves from videos/<token>.mp4 directory         │
│                                                         │
│  Token Mapping Logic:                                  │
│  ├─ Exact match: "hello" → hello.mp4 ✓               │
│  ├─ Stemming: "going" → "go" → go.mp4 ✓              │
│  ├─ Synonyms: "exam" → "test" → test.mp4 ✓           │
│  ├─ Fuzzy match: "helo" → "hello" → hello.mp4 ✓      │
│  └─ No match: "xyz" → ✗ (skipped, logged as missing)│
└─────────────────────────────────────────────────────────┘
```

---

## 📄 File Descriptions

### Core Extension Files

#### 1. **manifest.json**
- **Purpose**: Extension metadata and configuration
- **Size**: ~35 lines
- **Key Sections**:
  - `permissions`: activeTab, scripting, webRequest, storage
  - `host_permissions`: youtube.com, localhost:5000
  - `content_scripts`: Injects content.js on youtube.com
  - `background`: Service worker (background.js)
  - `action`: Extension popup (popup.html)
- **When it's used**: Browser loads this first, registers permissions and scripts

#### 2. **content.js** (Most Important!)
- **Purpose**: Main logic that runs on YouTube pages
- **Size**: ~290 lines
- **Key Functions**:
  - `initOverlay()`: Creates floating PiP window at bottom-right
  - `startCaptureCaptions()`: Sets up MutationObserver to detect caption changes
  - `processCaption(text)`: Sends caption to backend, gets tokens
  - `enqueueTokens(tokens)`: Adds tokens to FIFO queue
  - `playNextFromQueue()`: Plays next video clip, auto-advances
  - `updateCaption()`: Updates caption bar in overlay
  - `toggleCaptureCaptions()`: Start/stop caption detection
  - `clearQueue()`: Empty queue and stop playback
  - `chrome.runtime.onMessage` listener: Handles commands from popup
- **When it's loaded**: Browser injects this script into YouTube pages automatically
- **Data Flow**:
  ```
  MutationObserver detects caption
    ↓
  processCaption() sends to backend
    ↓
  Backend returns tokens
    ↓
  enqueueTokens() adds to queue
    ↓
  playNextFromQueue() starts playback
    ↓
  updateCaption() shows progress
  ```

#### 3. **popup.html**
- **Purpose**: Extension popup UI (shown when clicking extension icon)
- **Size**: ~80 lines
- **Elements**:
  - Backend URL input field (stores in chrome.storage.sync)
  - "Start Caption Capture" button
  - "Clear Queue" button
  - Help text with usage instructions
- **Styling**: Dark theme (blue accent), responsive
- **When it's used**: User clicks extension icon, popup appears

#### 4. **popup.js**
- **Purpose**: Event handlers for popup UI
- **Size**: ~20 lines
- **Key Listeners**:
  - Button clicks → send message to content.js
  - URL change → save to chrome.storage.sync
  - On load → restore saved URL from storage
- **When it's used**: When popup window is open
- **Communication**: Uses chrome.runtime.sendMessage to talk to content.js

#### 5. **background.js**
- **Purpose**: Service worker for extension lifecycle
- **Size**: ~3 lines (minimal)
- **Responsibilities**: 
  - onInstalled event handler
  - Can be extended for: persistent state, inter-script messaging, alarms
- **When it's used**: Runs in background when extension is active
- **Current State**: Minimal, placeholder for future features

---

## 🔄 Message Flow Diagram

### User Clicks "Start Caption Capture"
```
popup.html (button click)
    ↓
popup.js (event listener)
    ↓
chrome.runtime.sendMessage({action: 'toggleCaptions'})
    ↓
content.js (chrome.runtime.onMessage listener)
    ↓
startCaptureCaptions() function
    ↓
Set up MutationObserver on .captions-text
    ↓
Ready to detect caption changes!
```

### Caption Appears on YouTube
```
YouTube DOM updates with new caption
    ↓
MutationObserver (content.js) detects change
    ↓
processCaption() called with caption text
    ↓
fetch(POST /tokenize-text) to backend
    ↓
Backend returns: {tokens, missing, available}
    ↓
enqueueTokens(tokens) adds to queue
    ↓
playNextFromQueue() plays first clip
    ↓
Video element plays /token-video/<token>
    ↓
updateCaption() shows progress
    ↓
On video.ended → playNextFromQueue() advances
```

### User Changes Backend URL
```
popup.html (URL input)
    ↓
popup.js (onChange event)
    ↓
chrome.storage.sync.set({backendUrl})
    ↓
content.js checks storage.get() on page load
    ↓
Updates backendUrl variable
    ↓
All future fetch() calls use new URL
```

---

## 💾 Data Structures

### In Memory (content.js)
```javascript
// Global variables
let backendUrl = 'http://127.0.0.1:5000';  // URL to backend
let videoQueue = [];                        // [{token, url}, ...]
let isPlaying = false;                      // Playback state
let currentCaption = '';                    // Last caption text
let captionObserver = null;                 // MutationObserver ref
let overlayContainer = null;                // DOM ref to overlay

// Queue item structure
{
    token: 'we',
    url: 'http://127.0.0.1:5000/token-video/we'
}
```

### In Browser Storage (chrome.storage.sync)
```javascript
{
    backendUrl: 'http://127.0.0.1:5000'  // Saved by popup.js
}
```

### From Backend (API Response)
```json
{
    "tokens": ["we", "go", "college"],
    "tokens_all": ["we", "are", "go", "to", "college"],
    "missing": ["are", "to"],
    "available": ["we", "are", "go", "college", "hello", ...]
}
```

---

## 🔍 Execution Timeline

### Page Load
```
Time  | Event                      | Component    | State
------|----------------------------|--------------|------------------
0ms   | chrome://extensions loads  | manifest     | Register extension
10ms  | YouTube page loads         | content.js   | Script injected
50ms  | page.onload event fires    | content.js   | initOverlay() called
100ms | Overlay div created        | content.js   | DOM updated
150ms | Load backendUrl from store  | content.js   | backendUrl set
200ms | Overlay visible!           | Browser      | Ready for user
```

### User Clicks "Start Caption Capture"
```
Time  | Event                      | Component    | State
------|----------------------------|--------------|------------------
0ms   | Button click detected      | popup.js     | Event fired
5ms   | Message sent to content.js | popup        | chrome.runtime
10ms  | Message received           | content.js   | onMessage handler
15ms  | startCaptureCaptions()     | content.js   | Set up observer
20ms  | MutationObserver ready     | Browser      | Listening!
25ms  | "🎬 Starting caption..."   | console      | Logged
30ms  | User sees "enabled" state  | popup        | Button feedback
```

### Caption Appears
```
Time  | Event                      | Component    | Details
------|----------------------------|--------------|------------------
0ms   | Caption DOM updates        | YouTube      | Text added to span
5ms   | MutationObserver fires     | Browser      | Detected change
10ms  | processCaption() called    | content.js   | Text extracted
15ms  | POST /tokenize-text        | content.js   | Network request
50ms   | Backend processes         | app.py       | Tokenization
100ms | Response returned          | Backend      | tokens array
105ms | enqueueTokens() called     | content.js   | Queue updated
110ms | playNextFromQueue()        | content.js   | First clip starts
115ms | GET /token-video/we        | content.js   | Video download
150ms | Video plays in overlay     | Browser      | User sees PiP!
```

---

## 🔌 Integration Points

### With Backend
- **Endpoint**: POST /tokenize-text
  - Request: `{text: "caption"}`
  - Response: `{tokens, tokens_all, missing, available}`
  - Error: 400/500 handled gracefully

- **Endpoint**: GET /token-video/<token>
  - Returns: MP4 binary data
  - Status: 200 or 206 (Range request supported)
  - Error: 404 if token not found

### With YouTube
- **Target**: `.captions-text` DOM selector
- **Event**: MutationObserver on childList & subtree
- **Data**: Extracted from span.textContent

### With Chrome
- **APIs Used**:
  - chrome.runtime.sendMessage() → popup ↔ content
  - chrome.runtime.onMessage.addListener() → receive messages
  - chrome.storage.sync.get() → load URL
  - chrome.storage.sync.set() → save URL
  - chrome.tabs.query() → get active tab info
  - chrome.tabs.sendMessage() → send to specific tab

---

## ⚙️ Extension Lifecycle

### Install
1. User loads unpacked in chrome://extensions
2. Chrome reads manifest.json
3. Registers permissions & content scripts
4. Extension icon appears in toolbar

### On Each YouTube Page Visit
1. manifest.json matches URL pattern: youtube.com/*
2. Browser injects content.js automatically
3. content.js runs window.addEventListener('load', initOverlay)
4. Overlay initialized but caption capture is OFF
5. User must click popup button to activate

### Runtime
- Chrome.storage persists backend URL across sessions
- MutationObserver runs continuously (when enabled)
- Queue auto-advances through videos
- No server-side state needed (stateless)

### Uninstall
- User clicks remove button in chrome://extensions
- All data cleaned up automatically
- No leftover processes

---

## 🚀 Performance Optimizations

| Optimization | Implementation |
|--------------|-----------------|
| **Lazy Initialization** | Overlay created on page load, but observer only when needed |
| **Memory Efficient** | Queue stored in-memory, cleared after playback |
| **Network Caching** | Backend caches composed videos by hash (for segments mode) |
| **DOM Efficiency** | Single overlay div, updates via innerHTML only once |
| **Storage Optimization** | Only backend URL stored; auto-loads from chrome.storage.sync |
| **Debouncing** | MutationObserver fires on each caption change (not throttled, by design) |

---

## 🔐 Permissions Breakdown

| Permission | Why Needed | Risk Level |
|-----------|-----------|-----------|
| `activeTab` | Know which tab is active | ⚠️ Low |
| `scripting` | Inject content.js | ⚠️ Medium |
| `webRequest` | Monitor network (for future) | ⚠️ High |
| `storage` | Persist backend URL | ✅ Low |
| `host_permissions` youtube.com | Run on youtube.com | ⚠️ Medium |
| `host_permissions` localhost:5000 | Connect to backend | ✅ Low |

---

## 📊 Component Dependencies

```
manifest.json (root)
├── Depends on: Nothing (root config)
└── Required by: Chrome browser

popup.html (UI)
├── Depends on: popup.js, chrome.storage.sync
└── Required by: User interaction

popup.js (handlers)
├── Depends on: chrome.runtime, chrome.tabs
└── Required by: popup.html

content.js (main logic)
├── Depends on: chrome.storage.sync, chrome.runtime, backend API
└── Required by: YouTube pages

background.js (worker)
├── Depends on: Chrome extension API
└── Required by: Extension lifecycle

Backend (app.py)
├── Depends on: videos/*.mp4, models/*.pkl
└── Required by: content.js (fetch calls)
```

---

## ✅ Testing Each Component

| Component | Test Method | Expected Result |
|-----------|-----------|-----------------|
| manifest.json | Load unpacked | No errors, icon appears |
| content.js | Console logs | "Intellify content script loaded" |
| popup.html | Click icon | Popup appears with buttons |
| popup.js | Change URL, check storage | URL persisted after reload |
| background.js | chrome://extensions → Service workers | No errors |
| Integration | YouTube + captions | Videos play in overlay |

---

## 🎓 Key Concepts

### MutationObserver
- **What**: Browser API that watches DOM for changes
- **Why**: Detects when YouTube adds new captions
- **How**: Observes `.captions-text` element for childList changes
- **Trade-off**: Continuous observer uses ~1% CPU (acceptable)

### Message Passing
- **What**: Communication between popup and content script
- **Why**: Popup needs to control content.js behavior
- **How**: chrome.runtime.sendMessage() → chrome.runtime.onMessage.addListener()
- **Why not direct**: Different sandboxed contexts

### FIFO Queue
- **What**: First-In-First-Out array of {token, url} objects
- **Why**: Ensures videos play in order captions appear
- **How**: Array.push() to add, Array.shift() to remove
- **Alternative**: Could be priority queue (not needed here)

### HTTP Range Requests
- **What**: Client requests specific byte ranges of a file
- **Why**: Allows video streaming (206 Partial Content)
- **How**: Backend returns Content-Range headers
- **Benefit**: Faster playback, doesn't need full file first

---

**All components working together = Real-time sign language translation on YouTube!** 🤟

For detailed API documentation, see API_CONTRACT.md
For setup instructions, see README.md
For testing guide, see TESTING.md
