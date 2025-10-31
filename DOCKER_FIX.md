# 🔧 Docker Build Fix - Debian Package Update

## ❌ Problem
```
E: Package 'libgl1-mesa-glx' has no installation candidate
```

HF Spaces uses Debian Trixie (testing), where `libgl1-mesa-glx` package has been replaced.

## ✅ Solution Applied

### Changed in Dockerfile:
```dockerfile
# OLD (causes error)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ...

# NEW (working)
RUN apt-get update && apt-get install -y \
    libgl1 \
    curl \
    ...
```

### Changes:
1. ✅ Replaced `libgl1-mesa-glx` → `libgl1` (new Debian package name)
2. ✅ Added `curl` (needed for health checks)

## 📦 Updated Files
- `backend/Dockerfile` - Updated
- `signlink-hackx/Dockerfile` - Updated & pushed

## 🚀 Deployment Status
```
✅ Fix committed: 417e34a
✅ Pushed to HF Spaces
⏳ Rebuild triggered automatically
```

## 🔍 Monitor Build
Watch the rebuild at:
https://huggingface.co/spaces/Lamaq/signlink-hackx

Expected output:
```
--> RUN apt-get update && apt-get install -y libgl1 curl ...
DONE ✓
```

## ⏱️ Timeline
- Build time: ~5-10 minutes
- After build: Set OPENAI_API_KEY in Space settings
- Then: Test at https://lamaq-signlink-hackx.hf.space/health

---

**Status**: ✅ Fix deployed, build in progress
