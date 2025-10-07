# Use Python slim image
FROM python:3.11-slim

# Install system dependencies for face_recognition and dlib
RUN apt-get update && apt-get install -y \
    build-essential cmake libboost-all-dev \
    libopenblas-dev liblapack-dev libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all backend files
COPY . .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
