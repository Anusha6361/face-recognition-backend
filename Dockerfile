# Use Python slim image for a smaller final image
FROM python:3.11-slim

# Install system dependencies for face_recognition/dlib/PostgreSQL client
# This complex step is necessary for building dlib and its dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    # Add PostgreSQL client library for psycopg2 to function properly
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# --- Layer Caching Optimization ---
# Copy only requirements.txt first
COPY requirements.txt .

# Upgrade pip and install Python dependencies. This layer only rebuilds if requirements.txt changes.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application files (main.py, app/, service/, etc.)
# This layer rebuilds only when application code changes, saving time.
COPY . .

# Expose the port (Render handles mapping this)
EXPOSE 8000

# Command to run FastAPI using Gunicorn and Uvicorn workers (Production Ready)
# This provides process management, stability, and concurrency.
# Note: Adjust --workers if your instance has more/fewer cores (Gunicorn rule: 2 * CORE + 1)
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]