# Python Image
FROM python:3.11-slim

# Preventing Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFEred=1

# Working directory
WORKDIR /app

# Install system dependencies needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to take advantage of Docker layer caching
COPY requirements.txt .

# install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rerst of the application code
COPY . .

# Expose FastAPI's rest of the application code
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
