<<<<<<< HEAD
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git sqlite3 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
RUN mkdir -p /app/data /app/data/backups /app/data/reports /app/logs /app/config /app/modules
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "sovereign_daemon:app"]
=======
﻿FROM python:3.11-slim

# Install Tor and system build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    tor \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install Python dependencies including Tor routing
RUN pip install --no-cache-dir fastapi uvicorn pyjwt aiohttp websockets aiohttp-socks

# Expose API and WebSocket ports
EXPOSE 8000
EXPOSE 8765

# Set entrypoint execution rights
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
>>>>>>> 209b4c83 (Automated Deployment: Full SovereignCore structure)
