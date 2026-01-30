# Project Prism - SecOps Tool
# Python 3.10 Slim Base Image

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Create directories for persistent data
RUN mkdir -p /app/data /app/logs

# Expose ports
EXPOSE 8501
EXPOSE 5000

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run startup script
CMD ["/bin/bash", "/app/start.sh"]
