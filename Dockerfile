# Build stage - install dependencies that need compilation
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies for C extensions (numpy, aiohttp, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r /app/requirements.txt

# Final stage - slim runtime image
FROM python:3.9-slim

ARG BUILD_SHA=unknown
ARG BUILD_TIMESTAMP=unknown

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy the application code
COPY . /app

# Set environment variables
ENV WEB_CONCURRENCY=1
ENV PYTHONUNBUFFERED=1
ENV APP_BUILD_SHA=${BUILD_SHA}
ENV APP_BUILD_TIMESTAMP=${BUILD_TIMESTAMP}

# Expose port 80 for Flask
EXPOSE 80

# Command to run the application
CMD ["gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:80", "main:app"]