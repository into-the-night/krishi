# Use official Python image with full Linux distribution for better compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Redis and build tools
RUN apt-get update && apt-get install -y \
    redis-server \
    gcc \
    python3-dev \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install pip and dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose FastAPI and Redis ports
EXPOSE 8000 6379

# Create start script
RUN echo '#!/bin/bash\nredis-server --daemonize yes --bind 0.0.0.0\nuvicorn main:app --host 0.0.0.0 --port 8000' > /start.sh \
    && chmod +x /start.sh

# Start services using the startup script
CMD ["/start.sh"]