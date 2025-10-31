# 💾 Storage Changes for HF Spaces Deployment

## ⚠️ Critical Update

**Hugging Face Spaces uses ephemeral storage** - any files written during runtime are lost on Space restart or rebuild.

## ✅ Changes Made

### 1. Output Directory (Generated Videos/Images)
**Before:**
```python
OUTPUT_DIR = os.path.join(BACKEND_DIR, 'outputs')
```

**After:**
```python
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'signlink_outputs')
```

**Result**: Generated videos now go to `/tmp/signlink_outputs/` (ephemeral)

### 2. Video Cache (Downloaded WLASL Videos)
**Before:**
```python
videos_dir = os.path.join(BACKEND_DIR, 'videos')
cached_path = os.path.join(videos_dir, f"{token_lower}.mp4")
```

**After:**
```python
videos_cache_dir = os.path.join(tempfile.gettempdir(), 'signlink_videos')
cached_path = os.path.join(videos_cache_dir, f"{token_lower}.mp4")
```

**Result**: Videos downloaded from WLASL are cached in `/tmp/signlink_videos/` (ephemeral)

### 3. Deployment Script
**Removed**: Empty `outputs/` and `videos/` directory creation
**Added**: Note about ephemeral storage

## 🎯 What This Means

### ✅ Still Works
- Real-time gesture recognition (no file storage needed)
- Video generation (served immediately from memory/tmp)
- Chrome extension video fetching (downloads on-demand)
- Classroom WebSocket features (in-memory only)
- All API endpoints function normally

### ⚠️ Changed Behavior
- **Video cache is temporary**: Downloaded WLASL videos are re-fetched after restart
- **Generated videos expire**: Videos created via `/reverse-translate-video` are lost on restart
- **No persistent user data**: This is intentional and secure

### 💡 Performance Note
First request for a specific sign video will download from WLASL (may take 1-2 seconds). Subsequent requests use the `/tmp` cache until Space restarts.

## 🚀 Benefits

1. **HF Spaces Compatible**: No issues with read-only filesystem
2. **No Storage Limits**: Don't accumulate files over time
3. **Better Security**: No persistent user data
4. **Automatic Cleanup**: `/tmp` is cleared on restart

## 📝 No Action Required

These changes are already applied to `backend/app/main.py`. Just deploy normally:

```powershell
cd "C:\Users\lamaq\OneDrive\Desktop\MUJ REPO"
.\copy_to_hf.ps1
cd signlink-hackx
git add .
git commit -m "Deploy with ephemeral storage"
git push
```

## 🔍 Verification

After deployment, check logs for:
```
📁 Using temporary output directory: /tmp/signlink_outputs
⚠️ Note: Files in /tmp/signlink_outputs are ephemeral and will be lost on restart
```
