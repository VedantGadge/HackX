# Frontend - ASL Translation System

This is the frontend application for the ASL (American Sign Language) Translation System. It provides a clean, modern interface for real-time sign language detection and translation.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API running (see `../backend/README.md`)

### Installation

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Running the Development Server

```powershell
# Start the server
npm start

# Or with hot reload
npm run dev
```

The frontend will be available at **http://localhost:3000**

## 📁 Project Structure

```
frontend/
├── server.js           # Express server for development
├── package.json        # Node.js dependencies
├── static/             # Static assets
│   ├── script.js      # Main JavaScript (API calls, inference logic)
│   ├── style.css      # Main styles
│   ├── dropdown-fix.css
│   └── outputs/       # Generated video outputs
└── templates/          # HTML templates
    ├── index.html     # Main page (inference + video translation)
    ├── learn.html     # Learning mode
    ├── classroom_home.html
    ├── teacher.html   # Classroom teacher view
    └── student.html   # Classroom student view
```

## 🔧 Configuration

### API Connection

The frontend connects to the backend API using the URL configured in each HTML file. To change the backend URL:

**For Development (localhost):**
```javascript
// In templates/*.html, find this line:
window.API_BASE_URL = 'http://localhost:8000';
```

**For Production (deployed backend):**
```javascript
// Change to your deployed backend URL:
window.API_BASE_URL = 'https://your-backend.hf.space';
```

### Key Configuration Points

1. **index.html** (line ~475):
   ```html
   <script>
       window.API_BASE_URL = 'http://localhost:8000'; // Change this
   </script>
   ```

2. **script.js** uses this configuration:
   ```javascript
   const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';
   // All fetch calls use: fetch(`${API_BASE_URL}/endpoint`)
   ```

## 🌐 API Endpoints Used

The frontend communicates with these backend endpoints:

### Real-time Inference
- `POST /infer-frame` - Gesture detection
- `POST /infer-letter` - Letter detection (fingerspelling)

### Video Translation
- `POST /reverse-translate-video` - Full video generation
- `POST /reverse-translate-segment` - Segment generation
- `POST /tokenize-text` - Text to ASL tokens

### LLM Processing
- `POST /process-confirmed-words` - Convert gestures to English

### Status
- `GET /model-status` - Check ML model status
- `GET /health` - Health check

## 🎨 Features

### 1. Real-time ASL Detection
- **Gesture Mode**: Detects ASL words/signs
- **Letter Mode**: Detects fingerspelled letters
- Live camera feed with bounding boxes
- Confidence scores and word accumulation

### 2. Video Translation (English → ASL)
- Text input for translation
- Generates video from ASL sign library
- YouTube-style player with controls
- Segment-based playback

### 3. Classroom Feature
- Teacher can broadcast signs
- Students view in real-time
- Uses WebSocket for live connection

### 4. Learning Mode
- Interactive ASL alphabet practice
- Visual feedback and scoring

## 🛠️ Development

### Hot Reload
```powershell
npm run dev  # Uses nodemon for auto-restart
```

### Serving Static Files

The Express server (`server.js`) handles:
- Static files from `/static` folder
- HTML templates from `/templates` folder
- CORS for cross-origin requests

### Adding New Pages

1. Create HTML file in `templates/`
2. Add route in `server.js`:
   ```javascript
   app.get('/newpage', (req, res) => {
       res.sendFile(path.join(__dirname, 'templates', 'newpage.html'));
   });
   ```

### Modifying API Calls

All API calls in `script.js` use the `API_BASE_URL` constant:

```javascript
// Template for new API calls
const response = await fetch(`${API_BASE_URL}/your-endpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: value })
});
```

## 📦 Deployment

### Option 1: Vercel (Recommended)

1. Install Vercel CLI:
   ```powershell
   npm install -g vercel
   ```

2. Configure `vercel.json`:
   ```json
   {
     "version": 2,
     "builds": [
       { "src": "server.js", "use": "@vercel/node" }
     ],
     "routes": [
       { "src": "/(.*)", "dest": "/server.js" }
     ]
   }
   ```

3. Deploy:
   ```powershell
   vercel
   ```

4. Update `API_BASE_URL` to your backend URL

### Option 2: Static Hosting (Netlify, GitHub Pages)

If you want pure static hosting without Node.js:

1. Remove server.js dependency
2. Update HTML files to work as static files
3. Deploy static files directly
4. Configure `API_BASE_URL` to backend

### Option 3: Docker

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔍 Troubleshooting

### CORS Errors
```
Access to fetch at 'http://localhost:8000/infer-frame' from origin 'http://localhost:3000' has been blocked by CORS
```

**Solution**: Ensure backend has CORS enabled:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origin like "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Camera Not Working
```
NotAllowedError: Permission denied
```

**Solution**: 
- Use HTTPS in production
- Allow camera permissions in browser
- Check if camera is already in use

### Backend Connection Failed
```
TypeError: Failed to fetch
```

**Solution**:
- Check backend is running: `http://localhost:8000/health`
- Verify `API_BASE_URL` is correct
- Check network/firewall settings

### Static Files Not Loading
```
GET http://localhost:3000/static/script.js 404 (Not Found)
```

**Solution**:
- Ensure `npm install` was run
- Check file paths are correct
- Restart server: `npm start`

## 📝 Environment Variables

Create `.env` file (optional):
```env
PORT=3000
BACKEND_URL=http://localhost:8000
```

Update `server.js`:
```javascript
const PORT = process.env.PORT || 3000;
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Real-time gesture detection working
- [ ] Letter detection (fingerspelling) working
- [ ] Video translation generates clips
- [ ] Camera permissions granted
- [ ] All pages load correctly
- [ ] API calls succeed (check Network tab)
- [ ] CORS not blocking requests
- [ ] WebSocket classroom connection works

### Browser Console Checks

```javascript
// Check API connection
fetch('http://localhost:8000/health')
    .then(r => r.json())
    .then(console.log);

// Check camera access
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => console.log('Camera OK'))
    .catch(console.error);
```

## 📚 Additional Resources

- [FastAPI Backend Documentation](../backend/README.md)
- [API Documentation](../backend/API_DOCUMENTATION.md)
- [Deployment Guide](../deployment/DEPLOYMENT_GUIDE.md)

## 🤝 Contributing

1. Make changes in `static/` or `templates/`
2. Test locally with `npm run dev`
3. Ensure API calls use `API_BASE_URL`
4. Keep CORS configuration in mind
5. Test with both local and deployed backend

## 📄 License

This project is part of the ASL Translation System.
