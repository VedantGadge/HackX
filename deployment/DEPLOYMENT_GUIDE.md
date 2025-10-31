# Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Local Development

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variable
export OPENAI_API_KEY="your_key_here"  # Linux/Mac
# or
set OPENAI_API_KEY=your_key_here  # Windows

# 4. Run the server
python start.py
```

Access at: http://localhost:8000

### Option 2: Docker Deployment

```bash
# 1. Navigate to deployment folder
cd deployment

# 2. Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Build and run
docker-compose up -d

# 4. Check logs
docker-compose logs -f backend

# 5. Test
curl http://localhost:8000/health

# 6. Stop
docker-compose down
```

Access at:
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 3: Hugging Face Spaces

#### Step 1: Prepare Repository

```bash
# Create a new HF Space repository at https://huggingface.co/spaces

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy backend files
cp -r ../backend/* .

# Create app.yaml (already included as README.md in backend/)
```

#### Step 2: Configure Space

Go to your Space settings and add:

**Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key

**Space Settings:**
- SDK: Docker
- Port: 8000

#### Step 3: Deploy

```bash
# Commit and push
git add .
git commit -m "Initial deployment"
git push origin main
```

Your Space will automatically build and deploy!

## 📦 Required Files

### Backend Structure
```
backend/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── models/
│   ├── __init__.py
│   └── detr_model.py
├── services/
│   ├── __init__.py
│   ├── revtrans.py
│   └── dynamic_video_fetcher.py
├── utils/              # Copy from original project
├── pretrained/         # Add your .pkl models here
│   ├── gesture_model.pkl
│   └── letter_model.pkl
├── mapper/
│   └── WLASL_v0.3.json
├── requirements.txt
├── Dockerfile
├── start.py
└── README.md
```

### Frontend Structure
```
frontend/
├── templates/          # HTML files
├── static/            # CSS, JS, images
└── chrome_extension/  # Browser extension
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
BACKEND_PORT=8000
LOG_LEVEL=info
```

### Model Files

1. Place trained models in `backend/pretrained/`:
   - `gesture_model.pkl` - Gesture recognition
   - `letter_model.pkl` - Letter recognition

2. Place WLASL mapper in `backend/mapper/`:
   - `WLASL_v0.3.json` - Video dataset mapper

## 🧪 Testing

### Test Backend

```bash
cd backend
python test_backend.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Model status
curl http://localhost:8000/model-status

# Inference (requires image)
curl -X POST -F "frame=@test.jpg" http://localhost:8000/infer-frame
```

### Test WebSocket

Open browser console and run:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/classroom/TEST123/student');
ws.onmessage = (event) => console.log('Received:', event.data);
```

## 🐛 Troubleshooting

### Issue: Models not loading

**Solution:**
- Check if `.pkl` files exist in `backend/pretrained/`
- Verify file permissions
- Check logs: `docker-compose logs backend`

### Issue: CORS errors

**Solution:**
- Backend has CORS enabled for all origins
- Check if frontend is accessing correct URL
- Verify nginx proxy configuration (if using)

### Issue: WebSocket connection failed

**Solution:**
- Ensure WebSocket URL uses `ws://` (not `http://`)
- Check if port 8000 is accessible
- Verify no firewall blocking connections

### Issue: Video playback issues

**Solution:**
- Browser must support H.264 codec
- Check if output files exist in `backend/outputs/`
- Verify ffmpeg/opencv codecs installed

## 📊 Performance Optimization

### For Hugging Face Spaces

1. **Use CPU-optimized PyTorch:**
   ```bash
   pip install torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
   ```

2. **Reduce Model Size:**
   - Use smaller base models
   - Quantize models if possible
   - Cache frequently used videos

3. **Optimize Inference:**
   - Batch requests when possible
   - Use asyncio for concurrent requests
   - Implement request queuing

### Docker Optimization

1. **Multi-stage builds:**
   ```dockerfile
   FROM python:3.10-slim as builder
   # Install dependencies
   
   FROM python:3.10-slim
   COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
   ```

2. **Layer caching:**
   - Copy requirements.txt first
   - Install dependencies before copying code
   - Use .dockerignore to exclude unnecessary files

## 🔒 Security

### Production Checklist

- [ ] Set strong OPENAI_API_KEY
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add authentication for classroom feature
- [ ] Validate all user inputs
- [ ] Set up monitoring and logging
- [ ] Regular security updates

### Environment Variables

Never commit:
- `.env` files
- API keys
- Model files (if proprietary)

## 📈 Monitoring

### Health Checks

Backend includes health endpoint:
```bash
curl http://localhost:8000/health
```

Returns: `{"status": "ok", "model_loaded": true}`

### Logs

View logs:
```bash
# Docker
docker-compose logs -f backend

# Direct run
tail -f backend.log
```

## 🆘 Support

If you encounter issues:

1. Check logs first
2. Verify all dependencies installed
3. Test endpoints individually
4. Check GitHub Issues
5. Consult API documentation at `/docs`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces)
- [WLASL Dataset](https://github.com/dxli94/WLASL)
