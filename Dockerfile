# Use an official Python runtime as a parent image
# Switching to full image (not slim) to see if it resolves apt-get issues on Render
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set work directory
WORKDIR /app

# Install system dependencies with aggressive cleanup
USER root
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    apt-get update -y --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Expose port (Render uses 10000 by default)
EXPOSE 10000

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "backend.app:app"]
