#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""
import os
import sys

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting Sign Language Translator Backend (FastAPI)")
    print("=" * 60)
    print()
    print("📍 Server will run on: http://0.0.0.0:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Interactive API: http://localhost:8000/redoc")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
