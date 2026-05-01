# Alcruiter Backend — Production Docker Image
FROM python:3.10-slim

# System deps for psycopg2-binary, opencv-headless, pydub/ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the backend code
COPY backend/ ./backend/

# Ensure uploads directory exists
RUN mkdir -p /app/uploads /app/backend/uploads

# Render sets $PORT dynamically (default 10000)
ENV PORT=10000
EXPOSE ${PORT}

CMD gunicorn --chdir backend app:app \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --timeout 120
