# Base image: Python lightweight version
FROM python:3.8-slim

# Environment variables to prevent .pyc files and enable immediate output display
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    dcm2niix \
    libgl1 \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Install HD-BET separately (via pip)
RUN pip install hd-bet

# Copy project files into the container
COPY . /app

# Default entrypoint
ENTRYPOINT ["python", "trex.py"]