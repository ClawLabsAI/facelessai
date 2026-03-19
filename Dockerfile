FROM python:3.11-slim

# Cache bust - v3.0 - clipping support
RUN echo "build-v3.0"

# Install FFmpeg + yt-dlp dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
