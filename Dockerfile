FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the YOLO model so it isn't fetched at runtime on every cold start.
RUN mkdir -p /app/workout/static/models && \
    python -c "\
import urllib.request; \
urllib.request.urlretrieve( \
    'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt', \
    '/app/workout/static/models/yolov8n.pt' \
)"

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
