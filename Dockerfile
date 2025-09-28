# Multi-stage Docker build for RF Transceiver System
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY package*.json ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY src/ ./src/
COPY index.html ./

# Install dependencies and build
RUN npm ci
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code
COPY *.py ./
COPY 18_Real_RF_Transceiver_System/ ./18_Real_RF_Transceiver_System/

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    socat \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash rfuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from backend stage
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Copy application files
COPY --from=backend /app/*.py ./
COPY --from=backend /app/18_Real_RF_Transceiver_System/ ./18_Real_RF_Transceiver_System/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./static/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/certs
RUN chown -R rfuser:rfuser /app

# Switch to non-root user
USER rfuser

# Expose ports
EXPOSE 8765 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "server_real_rf_system.py", "--host", "0.0.0.0", "--wsport", "8765"]
