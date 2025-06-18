# V3 Zero-Touch Publishing Engine - Containerized KDP Publisher
FROM python:3.11-slim

# Install system dependencies for Chrome and Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY docker/requirements-docker.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Install Playwright browsers (Chrome) - use --force since Chrome is already installed
RUN playwright install --force chrome
RUN playwright install-deps chrome

# Copy application code
COPY kindlemint/ ./kindlemint/
COPY docker/kdp_publisher_task.py .
COPY docker/entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV DISPLAY=:99

# Expose health check endpoint
EXPOSE 8080

# Run the KDP publisher task
ENTRYPOINT ["./entrypoint.sh"]