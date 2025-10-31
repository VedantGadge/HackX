# Dockerfile for Sign Language Translator Backend
# Optimized for Hugging Face Spaces (ephemeral deployment)

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
# Note: libgl1-mesa-glx replaced with libgl1 in newer Debian
# Added ffmpeg for video encoding
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set matplotlib config directory to writable location
ENV MPLCONFIGDIR=/tmp/matplotlib

# Create necessary directories with proper permissions
RUN mkdir -p /tmp/matplotlib /tmp/signlink_outputs /tmp/signlink_videos && \
    chmod -R 777 /tmp/matplotlib /tmp/signlink_outputs /tmp/signlink_videos

# Expose port
EXPOSE 8000

# Run the application (no health check - HF Spaces handles this)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
