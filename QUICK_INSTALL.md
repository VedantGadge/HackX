# Intellify Chrome Extension - Quick Install (1 minute)

## ⚡ Super Quick Setup

### 1. Start Backend
```bash
cd d:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project
python app.py
```
Wait for: `Running on http://127.0.0.1:5000`

### 2. Load Extension
- Open Chrome → `chrome://extensions`
- Toggle **Developer mode** (top-right) ON
- Click **Load unpacked**
- Select: `d:\Final_Intellify\Intellify-Final-Project\Intellify-Final-Project\chrome_extension`
- ✅ Done!

### 3. Test It
- Go to youtube.com
- Find any video with captions (CC button available)
- Click extension icon → "Start Caption Capture"
- Play video
- Watch reverse translation clips play in bottom-right corner! 🎥➡️🤟

---

## 📖 Need More Details?

Read these files in order:
1. **EXTENSION_SETUP.md** (5-minute setup with troubleshooting)
2. **FILE_INVENTORY.md** (understand all files)
3. **chrome_extension/README.md** (full documentation)
4. **chrome_extension/TESTING.md** (testing checklist)

---

## 🐛 Something Wrong?

See **EXTENSION_SETUP.md** → Troubleshooting section

Or check:
- Backend running? → `python app.py` shows "Running on..."
- Extension loaded? → Icon appears in Chrome toolbar
- Captions enabled? → CC button clicked on YouTube
- Console logs? → F12 → Console tab → Look for "[Intellify]" messages
- Network requests? → F12 → Network tab → Look for /tokenize-text requests

---

**That's it! Enjoy real-time sign language translation on YouTube!** 🤟
