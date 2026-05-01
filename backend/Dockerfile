# Alcruiter Backend
FROM python:3.10-slim

# System deps for psycopg2-binary, opencv-headless, pydub/ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120"]